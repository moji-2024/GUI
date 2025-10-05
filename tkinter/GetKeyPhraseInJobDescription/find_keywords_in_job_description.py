from nltk.stem import SnowballStemmer
import pandas as pd
import re
stemmer = SnowballStemmer("english")

def find_keyword(key, list_skills):
    list_found = []
    for i, word in enumerate(list_skills):
        word = word.lower()
        if word == key.lower():
            list_found.append(word)
    return list_found



def find_moreThanOneWordINKeywordPhrase(listKeywords):
  return [phrase for phrase in listKeywords if len(phrase.split()) > 1]
def find_OneWordINKeywordPhrase(listKeywords):
  return  [phrase for phrase in listKeywords if len(phrase.split()) == 1]
def remove_repeatedPhraseWithSameMeaning(listKeywords):
  finalList = listKeywords.copy()
  moreThanOneWordINKeywordPhrase = find_moreThanOneWordINKeywordPhrase(listKeywords)
  OneWordINKeywordPhrase = find_OneWordINKeywordPhrase(listKeywords)
  for phrase in moreThanOneWordINKeywordPhrase:
    stemFirstWord = stemmer.stem(phrase.split()[0])
    for word in OneWordINKeywordPhrase:
      stemSingleWord = stemmer.stem(word)
      if stemFirstWord == stemSingleWord:
        try:
            finalList.remove(word)
        except ValueError:
            print(word,finalList)
  return finalList
def remove_keysInDictWithSameMeaning(dictKeywords):
  listFilteredKeywords =remove_repeatedPhraseWithSameMeaning(list(dictKeywords.keys()))
  finalDict = {}
  for key in dictKeywords:
    if key in listFilteredKeywords:
      finalDict[key] = dictKeywords[key]
  return finalDict
def create_comparison_table(resume, job_description, skills):
    dict_resume_keywords = {}
    dict_job_description_keywords = {}
    for word in skills:
        if len(word) > 3:
            stem_of_word = stemmer.stem(word)
            all_findings_in_job_description = re.findall(rf"\b\w*{stem_of_word}\w*\b", job_description,
                                                         flags=re.IGNORECASE)
            all_findings_in_resume = re.findall(rf"\b\w*{stem_of_word}\w*\b", resume, flags=re.IGNORECASE)
        else:
            all_findings_in_job_description = re.findall(fr'\b{word}\b', job_description, flags=re.IGNORECASE)
            all_findings_in_resume = re.findall(fr'\b{word}\b', resume, flags=re.IGNORECASE)
        if len(all_findings_in_job_description) > 0:
            dict_job_description_keywords[word] = len(all_findings_in_job_description)
            dict_resume_keywords[word] = len(all_findings_in_resume)
    return remove_keysInDictWithSameMeaning(dict_resume_keywords), remove_keysInDictWithSameMeaning(
        dict_job_description_keywords)
    # return dict_resume_keywords, dict_job_description_keywords


def find_keywordFrequency(resume, job_description,soft_skills,hard_Skills):
    dict_resume_soft_skills_keywords, dict_job_description_soft_skills_keywords = create_comparison_table(resume,
                                                                                                          job_description,
                                                                                                          soft_skills)
    dict_resume_hard_Skills_keywords, dict_job_description_hard_Skills_keywords = create_comparison_table(resume,
                                                                                                          job_description,
                                                                                                          hard_Skills)
    # create comparison df of skills
    df_softskills = pd.DataFrame({
        "Skill": dict_resume_soft_skills_keywords.keys(),
        "Resume": dict_resume_soft_skills_keywords.values(),
        "Job Description": dict_job_description_soft_skills_keywords.values()
    })

    df_hardskills = pd.DataFrame({
        "Skill": dict_resume_hard_Skills_keywords.keys(),
        "Resume": dict_resume_hard_Skills_keywords.values(),
        "Job Description": dict_job_description_hard_Skills_keywords.values()
    })
    df_softskills['Score'] = df_softskills.apply(lambda row: 1 - (
                abs(min(row['Resume'], row['Job Description']) - row['Job Description']) / row['Job Description']),
                                                 axis=1)
    df_hardskills['Score'] = df_hardskills.apply(lambda row: 1 - (
                abs(min(row['Resume'], row['Job Description']) - row['Job Description']) / row['Job Description']),
                                                 axis=1)
    final_score = round(((df_softskills['Score'].mean() + df_hardskills['Score'].mean()) / 2) * 100, 2)
    return df_softskills.sort_values(by="Job Description", ascending=False), df_hardskills.sort_values(
        by="Job Description", ascending=False), final_score


# soft, hard, score = find_keywordFrequency(resume, job_description)
# print('Soft skills')
# print(soft)
# print('------------------------------------------------------------------')
# print('Hard skills')
# print(hard)
# print('------------------------------------------------------------------')
# print(f'match Score is {score}')
