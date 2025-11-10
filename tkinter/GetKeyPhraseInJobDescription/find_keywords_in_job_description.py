from nltk.stem import SnowballStemmer
import pandas as pd
import re
from fuzzywuzzy import fuzz
stemmer = SnowballStemmer("english")

def find_keyword(key, list_skills):
    list_found = []
    for i, word in enumerate(list_skills):
        word = word.lower()
        if word == key.lower():
            list_found.append(word)
    return list_found

def removeRepeatedSkills(df:pd.DataFrame):
    df['countSkillWords'] = df['Skill'].str.split().str.len()
    df = df.sort_values(by='countSkillWords')
    df['Skill'] = df['Skill'].str.replace(r'\s{2,}', ' ', regex=True)
    listInd = []
    for ind, row in df.iterrows():
        stemskill = stemmer.stem(row['Skill'])
        Dfsearch = df[df['Skill'].str.contains(stemskill, case=False, na=False)]
        for i, rowSearch in Dfsearch.iterrows():
            if ind != i:
                if rowSearch['countSkillWords'] > row['countSkillWords']:
                    targetword = ' '.join(rowSearch['Skill'].split()[:row['countSkillWords']])
                    if stemmer.stem(targetword) == stemskill:
                        listInd.append(ind)
                        break
    df = df.drop(listInd, axis=0)
    df = df.drop('countSkillWords',axis=1)
    return df


def all_findings_Validator(phrase,l):
    finalList = []
    for w in l:
        if len(w) <= len(phrase):
            finalList.append(w)
        else:
            if fuzz.ratio(w, phrase) > 79:
                finalList.append(w)
    return finalList
def create_comparison_table(resume, job_description, skills):
    dict_resume_keywords = {}
    dict_job_description_keywords = {}
    for word in skills:
        all_findings_in_job_description = []
        if len(word) > 3:
            stem_of_word = stemmer.stem(word)

            all_findings_in_job_description = re.findall(rf"\b\w*{stem_of_word}\w*\b", job_description,
                                                         flags=re.IGNORECASE)
            all_findings_in_job_description = all_findings_Validator(word,all_findings_in_job_description)
            all_findings_in_resume = re.findall(rf"\b\w*{stem_of_word}\w*\b", resume, flags=re.IGNORECASE)
            all_findings_in_resume = all_findings_Validator(word,all_findings_in_resume)
        else:
            all_findings_in_job_description = re.findall(fr'\b{word}\b', job_description, flags=re.IGNORECASE)
            all_findings_in_resume = re.findall(fr'\b{word}\b', resume, flags=re.IGNORECASE)
        if len(all_findings_in_job_description) > 0:
            dict_job_description_keywords[word] = len(all_findings_in_job_description)
            dict_resume_keywords[word] = len(all_findings_in_resume)
    return dict_resume_keywords, dict_job_description_keywords


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
    filtered_softskills = removeRepeatedSkills(df_softskills)
    filtered_hardskills = removeRepeatedSkills(df_hardskills)

    filtered_softskills['Score'] = filtered_softskills.apply(lambda row: 1 - (
                abs(min(row['Resume'], row['Job Description']) - row['Job Description']) / row['Job Description']),
                                                 axis=1)
    filtered_hardskills['Score'] = filtered_hardskills.apply(lambda row: 1 - (
                abs(min(row['Resume'], row['Job Description']) - row['Job Description']) / row['Job Description']),
                                                 axis=1)
    final_score = round(((filtered_softskills['Score'].mean() + filtered_hardskills['Score'].mean()) / 2) * 100, 2)
    return filtered_softskills.sort_values(by="Job Description", ascending=False), filtered_hardskills.sort_values(
        by="Job Description", ascending=False), final_score
