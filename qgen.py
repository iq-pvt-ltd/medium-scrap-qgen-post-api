import nltk
# nltk.download('stopwords', download_dir='./nltk_data')
# nltk.download('popular', download_dir='./nltk_data')
import json
import pke
import string
# from summarizer import Summarizer
from nltk.corpus import stopwords
from flashtext import KeywordProcessor
from nltk.tokenize import sent_tokenize
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# nltk.download('stopwords')
# nltk.download('popular')



def output(urlId,full_text):
  qList = []

  output_qa = {
  "urlId":urlId,
  "questionType":"ONE_WORD",
  "question":qList
  }
  

  def get_nouns_multipartite(text):
    out=[]
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

  keywords = get_nouns_multipartite(full_text)
  filtered_keys=[]
  for keyword in keywords:
      if keyword.lower() in full_text.lower():
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
      sentences = [sentence.strip() for sentence in sentences if len(sentence) > 20]
      return sentences

  sentences = tokenize_sentences(full_text)

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
      delete = [key for key in keyword_sentences if len(keyword_sentences[key]) == 0]
      for key in delete: del keyword_sentences[key]
      return keyword_sentences

  keyword_sentence_mapping = get_sentences_for_keyword(filtered_keys, sentences)

  def format_inputs(context: str, answer: str):
      return f"{answer} \\n {context}"

  qList = []

  for keyword in keyword_sentence_mapping:
    text = format_inputs(keyword_sentence_mapping[keyword][0], keyword)
    input_ids = tokenizer(text, return_tensors="pt").input_ids
    generated_ids = mixQg_model.generate(input_ids, max_length=32, num_beams=4)
    output = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
    qa = {
      "question":output[0],
      "Answer":keyword
    }
    qList.append(qa)
  output_qa["question"] = qList
  # print(output_qa.jsonify())
  return output_qa





'''
Note:
Fast Api
Local download Model
JSON :
{
  "urlId":"12345667889",
  "questionType":"FILL_BLANK",
  "questions":[
    {
      "question":"what is ...",
      "answer":"ans"
      
    },
    {
      "question":"what is ...",
      "answer":"ans"
      
    }
    ]
}


'''