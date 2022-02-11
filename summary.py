import json
from transformers import AutoConfig, AutoTokenizer, AutoModel
from summarizer import Summarizer
from transformers import logging
logging.set_verbosity_error()


def summary(mediumText):
    '''
    SUMMARY FUNCTION
    '''
    PATH = './Sum_Model/bert-large-uncased/'
    custom_config = AutoConfig.from_pretrained(PATH)
    custom_config.output_hidden_states = True
    custom_tokenizer = AutoTokenizer.from_pretrained(PATH)
    custom_model = AutoModel.from_pretrained(PATH, config=custom_config)

    Sum_model = Summarizer(custom_model=custom_model,
                           custom_tokenizer=custom_tokenizer)
                           
    summary_content = Sum_model(mediumText, ratio=0.5)
    fullSummarizedContent = ''.join(summary_content)
    summarizedContent = {"summaryContent": fullSummarizedContent}
    Json_summarizedContent = json.dumps(summarizedContent, indent=2)
    ''''
        Returns the JSON data
    '''
    return json.loads(Json_summarizedContent)
