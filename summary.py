import json
import summarizer
from transformers import AutoTokenizer, AutoModelForMaskedLM
from summarizer import Summarizer
from transformers import logging
logging.set_verbosity_error()


def summary(contentMedium):
    '''
    SUMMARY FUNCTION
    '''
    PATH = '/content/bert-large-uncased'
    summary_model = AutoModelForMaskedLM.from_pretrained("bert-large-uncased")
    summary_model = Summarizer()
    summary_content = summary_model(contentMedium, ratio=0.5)
    fullSummarizedContent = ''.join(summary_content)
    summarizedContent = {"summaryContent": fullSummarizedContent}
    Json_summarizedContent = json.dumps(summarizedContent, indent=2)
    ''''
     Returns the JSON data
    '''
    return json.loads(Json_summarizedContent)
