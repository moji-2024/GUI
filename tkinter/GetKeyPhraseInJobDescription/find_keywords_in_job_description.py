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
            all_findings_in_job_description = [w for w in all_findings_in_job_description if len(w) <= len(word)]
            all_findings_in_resume = re.findall(rf"\b\w*{stem_of_word}\w*\b", resume, flags=re.IGNORECASE)
            all_findings_in_resume = [w for w in all_findings_in_resume if len(w) <= len(word)]
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

resume= '''Moji Shaban
Calgary, AB, Canada | +1-(403)-925-4989 | shaban.mojtaba2014@gmail.com | linkedin.com/in/mojtaba-shaban-analyst
PROFESSIONAL SUMMARY
5+ years of combined experience in retail operations, customer service, and data analytics, with proven ability to improve efficiency and enhance customer experiences
Skilled in Python (NumPy, pandas, matplotlib), SQL, Excel, Tableau, and Power BI to clean, analyze, and visualize data into actionable insights for business and research use
Organized product displays and tracked inventory with precision and strong attention to detail, reducing errors and improving the overall shopping experience.
Oversaw daily retail management operations to maintain smooth business performance and ensure compliance with company standards.
Analyzed sales and inventory data using Excel to identify trends and improve restocking accuracy.
Forecasted product demand to minimize stockouts, optimize seasonal sales strategies, and align performance with financial goals.
Currently enrolled in NPower Canada’s Junior Data Analyst Program (Aug–Nov 2025) to further strengthen data visualization, database management, and applied statistical skills
Fluent in English and earned CELPIP (Canadian English Language Proficiency Index Program): 
Overall Score 7  
TECHNICAL SKILLS
Programming Languages: Python (Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn, TensorFlow, Re), R (ggplot2), SQL, Bash
Operating Systems: Windows, Linux (Ubuntu)
Software, Applications, Tools: IBM Watson Studio, Schrödinger Suite (Maestro, Glide, Phase, Desmond), Jupyter Notebook, Microsoft Office (Excel, Word, PowerPoint), Git, GitHub
Databases: MySQL, SQLite, MongoDB
Visualization Tools: Matplotlib, Seaborn, ggplot2, IBM Cognos Analytics
Cloud Computing: IBM Cloud, Google Colab
Project Management: Agile, Waterfall, Scrum, Trello
Skills: Data wrangling and preprocessing, data cleaning, data visualization and dashboarding, statistical analysis, machine learning model development, data prediction, storytelling, web scraping, cheminformatics, critical thinking
EDUCATION & CERTIFICATIONS 
Microsoft Azure AI900 Professional Certificate                                                                   Aug 2025 - Sep 2025 NPower Canada | Calgary, AB
Junior Data Analyst Program                                                                                                Aug 2025 - Nov 2025 NPower Canada | Calgary
IBM Data Analyst Professional Certificate                                                                          Aug 2025 - Nov 2025
Coursera | Remote
M.Sc. in Biochemistry                                                                                                              Sep 2016 - Sep 2018
Shahid Bahonar University of Kerman | Kerman, Iran 
B.Sc. in Biology – Animal Science                                                                                            Sep 2012 - Jul 2016
Shahid Bahonar University of Kerman | Kerman, Iran

PROFESSIONAL EXPERIENCE 
Sales Associate / Store Operations Assistant                                                                      July 2023 – May 2025
Sina Footwear | Calgary, AB
Managed both physical and online store platforms, ensuring accurate product listings, timely updates, and consistent branding that enhanced customer experience and increased repeat visits
Demonstrated strong time management by adapting to changing customer needs and dynamic merchandising in fast-paced store operations while maintaining service quality during peak hours.
Conducted sales, inventory, and marketing analysis using Excel to improve stock accuracy and support operational planning.
Consulted with managers on presentation standards and operational improvements to ensure compliance with company policies and enhance workflow efficiency.
Provided data-driven consulting by analyzing customer preferences and recommending merchandising adjustments to improve sales performance.
Resolved customer concerns through effective problem-solving skills, strengthening loyalty and encouraging repeat business.
Assisted in financial reporting and basic forecasting to support store budgeting and seasonal demand planning. 
Forecasted product demand to minimize stockouts, optimize seasonal sales strategies, and align performance with financial goals.
Coded and developed a custom desktop BI application to automate sales tracking, data exports, and reporting, reducing manual recordkeeping time by 40%.
Created and maintained visual documentation and reports to support communication and decision-making.
Processed, transformed, and cleaned raw product and sales data as part of the BI data pipeline, ensuring accurate and up-to-date information across platforms.
Applied effective time management while independently handling daily store operations and 50+ customer interactions across in-person and phone support, ensuring timely issue resolution and smooth workflows.
Created business-intelligence reports and visual summaries using Excel and Python to support operational decisions.

VOLUNTEER EXPERIENCE 
Chess Program Volunteer / Trainer                                                                                        July 2024 - Present
Checkmate Foundation | Calgary, AB
Train participants in chess strategies and techniques, improving the skills and fostering critical thinking and problem-solving abilities
Assist in setting up and managing chess boards and events, ensuring smooth execution and efficient
program operations

Data Analyst                                                                                                                            Apr 2024 - Sep 2024
BIDAR | Toronto, Ontario, remote
Responsible for enhancing database organization and accessibility by clustering descriptive data and cleaning nonsensical entries in MongoDB
Collaborated with team members to streamline data workflows and document procedures for improved data quality and operational efficiency.

PROJECTS
Prepared project documentation and GitHub repositories to ensure reproducibility.
Deep Learning Model for Image-based Prediction 		           		             	          Aug 2025 
Developed a multi-layer neural network in Python with custom activation functions, backpropagation, and image preprocessing, achieving convergence over 6,000 iterations and visualizing performance metrics 
Project Link: https://github.com/moji-2024/deep-learning_DNN 
 
Text Classification Using K-Means Clustering   | Bidar Company | Remote                 	Apr 2024 - Sep 2024
Collected, transformed, and organized multi-source data to build BI dashboards and generate insights for management.
Applied K-means clustering with Python (pandas, scikit-learn) to classify and analyze large text datasets, improving clustering accuracy through preprocessing and generating actionable insights for reporting and decision-making. 
 
DataMapperPro                                                                                                                  	Jun 2024 - Aug 2024 
Developed an ORM system in Python to facilitate robust database handling, demonstrating practical application of programming skills for data management. 
Project Link: https://github.com/moji-2024/DataMapperPro 
 
AutoLedger | Sina Footwear Company | Calgary   			      	      	   Sep 2023 - Nov 2023 
Built a Tkinter-based desktop GUI integrated with SQLite to manage shoe sales, automate receipts, enable data filtering, and generate real-time reports  
 Project Link: https://github.com/moji-2024/GUI/tree/main/tkinter/Sina_footwear 



'''
job_description = '''
Platform Maintenance and Development
- Assist the Data Team, Data/AI Consultant, and Data Platform Vendor by gathering and preparing
information needed to maintain and enhance the Data Platform.
- Help monitor data quality and identify basic data issues, escalating them to senior team members or
external partners for resolution.
- Support the preparation and updating of platform documentation, including data flow diagrams,
standard operating procedures, and user guides.
- Contribute to the creation and maintenance of Power BI dashboards and reports by providing data
extracts, preparing draft visuals, and performing data checks as directed.
- Assist in collecting and organizing feedback from business users to help inform future platform
improvements.
- Provide administrative and coordination support to project activities, including scheduling and
coordinating meetings, circulating documents for review and approval, processing project-related
invoices, and updating project budget tracking documents.

Data Analysis
- Help extract and prepare data sets for analysis under the direction of the Data Team or Data/AI
Consultant.
- Assist in updating and maintaining Power BI dashboards and reports used for operational and
managerial purposes.
- Prepare draft data visualizations and summaries to support exploratory analysis and reporting needs.
- Support ad-hoc data requests by gathering data, preparing initial analysis, and documenting results
for review by senior team members.
- Help collect and document reporting requirements from business stakeholders to support the
development of new dashboards or reports.
- Contribute to the clear presentation of findings by preparing draft charts, summaries, or written
content for reports and presentations.
- Other duties as required to accurately support our business and operations and the responsibilities
of the Integration Division of the organization.
- Provide support to the personnel responsible in data collection and analysis, management of data
and documents, and optimization of shared folders. Proactively contributes to improvement efforts
by identifying issues and proposing effective solutions.

Other duties as required

Minimum Requirements:

Education:
- Bachelor’s degree in Mathematics, Business, Economics, or a related quantitative discipline.

Experience:
- Minimum of 2 years of experience writing SQL code to support reporting, data transformation, or
analytics.
- Foundational experience with data modelling and developing dashboards in Power BI.
- Basic understanding of data transformation processes and ETL concepts.
- Familiarity with Snowflake and Power BI and relational databases is considered an asset

Skills:
- Ability to adapt to a changing work environment; as well as the ability to learn new tasks easily.
- Time management skills are essential. Sound independent judgment to plan, prioritize, and organize
a diversified workload. Perform well under pressure and able to multi-task and meet multiple
deadlines.
- Solid understanding of data fundamentals and ability to apply them under guidance.
- Ability to quickly create draft visualizations to explore data trends.
- Effective analytical and problem-solving skills with attention to detail.
- Strong written and verbal communication skills, including the ability to explain technical information
to non-technical audiences.
- Collaborative mindset and ability to work effectively as part of cross-functional teams.


# '''
# import os,json
# with open(os.path.join("jsonDataBase", 'hard_Skills.json'), "r") as f:
#     hard_Skills = json.load(f)
# with open(os.path.join("jsonDataBase", 'soft_Skills.json'), "r") as f:
#     soft_Skills = json.load(f)
# soft, hard, score = find_keywordFrequency(resume, job_description,soft_Skills,hard_Skills)
# print('Soft skills')
# print(soft)
# print('------------------------------------------------------------------')
# print('Hard skills')
# print(hard)
# print('------------------------------------------------------------------')
# print(f'match Score is {score}')
