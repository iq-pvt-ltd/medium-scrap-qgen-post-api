import os
import nltk
import pke
import string
import requests
from google.cloud import storage
import google.cloud.storage
from nltk.corpus import stopwords
from flashtext import KeywordProcessor
from nltk.tokenize import sent_tokenize
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


def output(urlId, full_text, title, summary):
    ''''
    Q_GENERATOR FUNCTION-->Hugging Face
    '''
    print(".....Entering Q-gen.......")

    def get_nouns_multipartite(text):
        out = []
        extractor = pke.unsupervised.MultipartiteRank()
        extractor.load_document(input=text, language='en')
        pos = {'PROPN'}
        stoplist = list(string.punctuation)
        stoplist += ['-lrb-', '-rrb-', '-lcb-', '-rcb-', '-lsb-', '-rsb-']
        stoplist += stopwords.words('english')
        extractor.candidate_selection(pos=pos, stoplist=stoplist)
        extractor.candidate_weighting(alpha=1.1,
                                      threshold=0.75,
                                      method='average')
        keyphrases = extractor.get_n_best(n=20)
        for key in keyphrases:
            out.append(key[0])
        return out

    keywords = get_nouns_multipartite(summary)
    filtered_keys = []
    for keyword in keywords:
        if keyword.lower() in summary.lower():
            filtered_keys.append(keyword)

    """
      MixQGen Starts here
  """
    PATH = "./models/mixqg-large/"
    tokenizer = AutoTokenizer.from_pretrained(PATH)
    mixQg_model = AutoModelForSeq2SeqLM.from_pretrained(PATH)

    def tokenize_sentences(text):
        sentences = [sent_tokenize(text)]
        sentences = [y for x in sentences for y in x]
        # Remove any short sentences less than 20 letters.
        sentences = [sentence.strip()
                     for sentence in sentences if len(sentence) > 20]
        return sentences

    sentences = tokenize_sentences(summary)

    def get_sentences_for_keyword(keywords, sentences):
        keyword_processor = KeywordProcessor()
        keyword_sentences = {}
        for word in keywords:
            keyword_sentences[word] = []
            keyword_processor.add_keyword(word)

        for sentence in sentences:
            keywords_found = keyword_processor.extract_keywords(sentence)
            set_keywords_found = set(keywords_found)
            keywords_found = list(set_keywords_found)
            if(len(keywords_found) > 0):
                for key in keywords_found:
                    keyword_sentences[key].append(sentence)

        for key in keyword_sentences.keys():
            values = keyword_sentences[key]
            values = sorted(values, key=len, reverse=True)
            keyword_sentences[key] = values

        # Delete keys which does not have sentences
        delete = [key for key in keyword_sentences if len(
            keyword_sentences[key]) == 0]
        for key in delete:
            del keyword_sentences[key]
        return keyword_sentences

    keyword_sentence_mapping = get_sentences_for_keyword(
        filtered_keys, sentences)

    def format_inputs(context: str, answer: str):
        return f"{answer} \\n {context}"

    qList = []

    output_qa = {
        "urlId": urlId,
        "keywords": filtered_keys,
        "questionType": "ONE_WORD",
        "questions": qList
    }

    for keyword in keyword_sentence_mapping:
        text = format_inputs(keyword_sentence_mapping[keyword][0], keyword)
        input_ids = tokenizer(text, return_tensors="pt").input_ids
        generated_ids = mixQg_model.generate(
            input_ids, max_length=32, num_beams=4)
        output = tokenizer.batch_decode(
            generated_ids, skip_special_tokens=True)
        qa = {
            "question": output[0],
            "answer": keyword
        }
        qList.append(qa)
    output_qa["questions"] = qList

    '''
    Uploading to GCS
    '''
    BUCKET_NAME = os.getenv('GCP_BUCKET_NAME')
    print(".....Uploading to Bucket.......")
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(BUCKET_NAME)
    fileName = "{}.txt".format(urlId)
    blob = bucket.blob(fileName)
    blob.upload_from_string(
        "{}<->{}<->{}<->{}".format(title, filtered_keys, full_text,summary))
    print(".....Uploaded to Bucket.......")

    ''''
    POST THE QUESTIONS TO THE DATABASE
    '''

    DATABASE_API_ENDPOINT = os.getenv('CLOUD_TRIGGER_URL')
    API_ENDPOINT = "{}/core/question-generations/complete-task"
    postDB = API_ENDPOINT.format(DATABASE_API_ENDPOINT)
    req = requests.post(url=postDB, json=output_qa)

    if req.status_code != 204:
        print("Error:", req.status_code, "occurred")
    else:
        '''
        FINISH PROCESS AND RETURNS MESSAGE
        '''
        print("......Exiting Q_gen.....")
        return {"Message": "Generated Questions and Updated in DataBase"}
