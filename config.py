"""
here you have to specify the path to your data folder
"""
path_to_crime_data = "data/met_data"

"""
when release or partial submission set to False
"""
DEV_EXPERIMENTAL = False

"""
here you need to specify the last available data, should be the link of form: "https://data.police.uk/data/archive/2024-03.zip"
"""
LAST_AVAILABLE_DATASET = None 

### NON-CHANGEABLE CONFIGURATIONS ###

# global variables

questions_dict = {
    # 21 - 19 questions
    'Q13': ['To what extent are you worried about… Crime in this area? If necessary: By your area I mean 15 minutes walk from your home.', 'worries about crime near citizens'],
    'Q15': ['To what extent are you worried about Anti-social behaviour?', 'worries about anti-social behaviour'],
    'Q60': ['Taking everything into account, how good a job do you think the police IN YOUR AREA are doing?', 'police works good in your area'],
    'Q61': ['Taking everything into account, how good a job do you think the police IN LONDON AS A WHOLE are doing?', 'police works good in London'],
    'Q62A': ['To what extent do you agree with these statements about the police in your area? By "your area" I mean within 15 minutes\' walk from your home. They can be relied on to be there when you need them.', 'police reliability in your area'],
    'Q62C': ['To what extent do you agree with these statements about the police in your area? By "your area" I mean within 15 minutes\' walk from your home. The police in your area treat everyone fairly regardless of who they are.', 'police fairness in your area'],
    'Q62F': ['To what extent do you agree with these statements about the police in your area? By "your area" I mean within 15 minutes\' walk from your home. They are dealing with the things that matter to people in this community.', 'police addressing community issues'],
    'Q62TG': ['To what extent do you agree with these statements about the police in your area? By "your area" I mean within 15 minutes\' walk from your home. The police in your area listen to the concerns of local people.', 'police listen to local concerns'],
    'A121': ['How confident are you that the Police in your area use their stop and search powers fairly?', 'confidence in fair use of stop and search'],
    'NQ135BD': ['To what extent do you agree or disagree with the following statements: The Metropolitan Police Service is an organisation that I can trust.', 'trust in the Metropolitan Police Service'],
    'NQ135BE': ['To what extent do you agree or disagree with the following statements: It is important that the Metropolitan Police Service’s workforce reflects the population profile of the communities it serves.', 'importance of workforce diversity in police'],
    'NQ135BF': ['The police in your local area currently reflect the population profile of the local community?', 'police reflect local community profile'],
    'NQ135BG': ['Senior ranking officers in the Metropolitan Police Service reflect the population profile of London.', 'senior officers reflect London\'s profile'],
    'NQ62D': ['The police have the same sense of right and wrong as I do.', 'shared values with police'],
    'NQ135BH': ['To what extent do you agree or disagree that the police in your local area are sufficiently held accountable for their actions?', 'police accountability in your area'],
    'XQ122B': ['How confident are you that the Metropolitan Police Service deal fairly with complaints made about them?', 'confidence in fair handling of complaints'],
    'Q131': ['How well informed do you feel about what the police in YOUR AREA have been doing over the last 12 months?', 'knowledge of local police activities'],
    'Q133': ['How well informed do you feel about what the police in LONDON AS A WHOLE have been doing over the last 12 months?', 'knowledge of police activities in London'],
    'NPQ135A': ['What would you say are the top three things that the police should be dealing with IN YOUR AREA?', 'top police priorities in your area'],
    'NNQ135A': ['What would you say are the top three things that the police should be dealing with across LONDON?', 'top police priorities in London'],
    'XNQ135B': ['Across London, there are groups of community volunteers who work together with the police to make sure they follow best practice. Their roles include visiting custody suites to check on the treatment of detainees and reviewing how the police use their Stop and Search powers. To what extent do you agree or disagree that using volunteers in this way makes you feel reassured that the police are held to account?', 'volunteer involvement reassures police accountability'],
    'ReNQ147': ['Are you Asian, Black, of a mixed background, White, or of another ethnic group? And is that...?', 'self-identified ethnicity'],
    'XQ3A': ['Call the police to report a crime occurring in your local area (the values are added as a note).', 'reporting local crime'],
    'XQ8': ['Overall, how confident, if at all, are you that…? …The criminal justice system is effective in bringing people who commit crimes to justice.', 'confidence in criminal justice system'],
    'NQ21': ['If you are walking alone in this area and you see a police officer on foot, bicycle or horseback, does it make you feel more safe, less safe or does it make no difference?', 'feeling of safety seeing a police officer'],
    'Q21': ['How safe do you feel walking alone in this area after dark?', 'safety walking alone after dark'],
    'Q54A': ['On the LAST OCCASION, how safe did you feel on a bus?', 'safety on bus'],
    'Q54B': ['On the LAST OCCASION, how safe did you feel on the tube/underground?', 'safety on tube/underground'],
    'Q54C': ['On the LAST OCCASION, how safe did you feel on a train/tram?', 'safety on train/tram'],
    'Q54D': ['On the LAST OCCASION, how safe did you feel in a black cab?', 'safety in black cab'],
    'Q54E': ['On the LAST OCCASION, how safe did you feel in a taxi?', 'safety in taxi'],
    'NQ57AA': ['How satisfied are you with the policing of the following London transport networks? Bus network', 'satisfaction with bus network policing'],
    'NQ57AB': ['How satisfied are you with the policing of the following London transport networks? Tube/London Underground Network.', 'satisfaction with tube network policing'],
    'NQ57AC': ['How satisfied are you with the policing of the following London transport networks? Train Network.', 'satisfaction with train network policing'],
    'NQ57AD': ['How satisfied are you with the policing of the following London transport networks? Docklands Light Railway.', 'satisfaction with Docklands Light Railway policing'],
    'NQ57AE': ['How satisfied are you with the policing of the following London transport networks? Tram Network.', 'satisfaction with tram network policing'],
    'NQ44A': ['To what extent do you think hate crime is a problem in this area? By hate crime we mean people who are subject to attack/abuse because of their skin colour, ethnic origin, religion, disability or sexual orientation.', 'hate crime problem in area'],
    'NQ48A': ['To what extent do you think that online harassment and cyber-bullying are a problem?', 'online harassment and cyber-bullying problem'],
    'NQ49B': ['To what extent do you feel sexual assault or sexual violence is a problem in this area?', 'sexual assault/violence problem in area'],
    'Q58': ['To what extent are you worried about a TERRORIST ATTACK in London?', 'worries about terrorist attack in London'],
    'Q59': ['And to what extent are you worried about a TERRORIST ATTACK particularly in this area?', 'worries about terrorist attack in area'],
    'Q62D': ['To what extent do you agree with these statements about the police in this area? By "this area" I mean within 15 minutes\' walk from here. They can be relied on to deal with minor crimes.', 'police deal with minor crimes'],
    'Q62E': ['To what extent do you agree with these statements about the police in this area? By "this area" I mean within 15 minutes\' walk from here. They understand the issues that affect this community.', 'police understand community issues'],
    'Q62H': ['To what extent do you agree with these statements about the police in this area? By "this area" I mean within 15 minutes\' walk from here. The police in this area are helpful.', 'police are helpful in area'],
    'Q62TJ': ['To what extent do you agree with these statements about the police in this area? By "this area" I mean within 15 minutes\' walk from here. The police in this area are easy to contact.', 'police are easy to contact'],
    'NQ62A': ['To what extent do you agree with these statements about the police and crime more generally? Respect for the police is an important value for people to have.', 'importance of respecting police'],
    'XQ81': ['When thinking about the role of the police, which of the following aspects do you think should be most important?', 'most important aspects of police role'],
    'Q79A': ['And how well do you think the Metropolitan Police... Prevents terrorism?', 'police prevent terrorism'],
    'Q79B': ['Please use a scale of 1 to 7, where 1 = Not at all well and 7 = Very well And how well do you think the Metropolitan Police …Respond to emergencies promptly? Please think of London as a whole, rather than your local area in this instance.', 'police respond to emergencies promptly'],
    'Q79C': ['And how well do you think the Metropolitan Police... Provide a visible patrolling presence?', 'police visibility'],
    'Q79D': ['Please use a scale of 1 to 7, where 1 = Not at all well and 7 = Very well And how well do you think the Metropolitan Police …Tackle gun crime? Please think of London as a whole, rather than your local area in this instance.', 'police tackle gun crime'],
    'NQ79D': ['And how well do you think the Metropolitan Police... Tackle knife crime?', 'police tackle knife crime'],
    'Q79E': ['Please use a scale of 1 to 7, where 1 = Not at all well and 7 = Very well And how well do you think the Metropolitan Police …Support victims and witnesses? Please think of London as a whole, rather than your local area in this instance.', 'police support victims and witnesses'],
    'Q79F': ['And how well do you think the Metropolitan Police... Police major events in London?', 'police major events'],
    'Q79G': ['Please use a scale of 1 to 7, where 1 = Not at all well and 7 = Very well How well do you think the Metropolitan Police… Tackle drug dealing and drug use? If necessary: Please think of London as a whole, rather than your local area in this instance.', 'police tackle drug dealing and use'],
    'Q79H': ['And how well do you think the Metropolitan Police... Tackle dangerous driving?', 'police tackle dangerous driving'],
    'Q79I': ['Please use a scale of 1 to 7, where 1 = Not at all well and 7 = Very well And how well do you think the Metropolitan Police ……Respond to hate crime? Please think of London as a whole, rather than your local area in this instance.', 'police respond to hate crime'],
    'Q79J': ['Please use a scale of 1 to 7, where 1 = Not at all well and 7 = Very well How well do you think the Metropolitan Police… Respond to violence against women and girls? If necessary: Please think of London as a whole, rather than your local area in this instance.', 'police respond to violence against women and girls'],
    'NQ79BC': ['I would like to get your opinion on the use of body cameras worn by officers. To what extent do you agree or disagree with the following statements about the cameras...? The cameras reassure me that the police will do the right thing.', 'body cameras reassure proper police conduct'],
    'NQ79BD': ['I would like to get your opinion on the use of body cameras worn by officers. To what extent do you agree or disagree with the following statements about the cameras...? The cameras make officers treat people fairly.', 'body cameras ensure fair treatment'],
    'SQ79B': ['To what extent do you agree or disagree with the following statements: It makes me feel safer when I see a police officer with a firearm.', 'feeling safer with armed officers'],
    'SQ79C': ['To what extent do you agree or disagree with the following statements: If I saw an officer with a firearm I would feel comfortable approaching them.', 'comfort approaching armed officers'],
    'XQ106B': ['When you contacted the police on this occasion, do you feel you were treated with respect by the police officers involved?', 'treated with respect by police'],
    'XQ122': ['Have you ever been dissatisfied with the way a Metropolitan Police officer behaved towards you or someone you know?', 'dissatisfaction with police behavior'],
    'PQ135AA': ['What would you say are the top three things that the police should be dealing with in your area?', 'top three police priorities'],
    'PQ135AZ': ['What would you say are the top three things that the police should be dealing with in your area?', 'top three police priorities'],
    'PQ135AAA': ['What would you say are the top three things that the police should be dealing with in your area?', 'top three police priorities'],
    'PQ135AAY': ['What would you say are the top three things that the police should be dealing with in your area?', 'top three police priorities'],
    # additional questions about ethnicity for 21 - 15
    'Q39A_2': ['To what extent do you think knife crime is a problem in this area? By knife crime I mean people carrying or using knives to threaten or commit violence.', 'knife crime problem in area']
}

# Define the weights for each category
weights = {
    'Strongly disagree': 0,
    'Disagree': 0.25,
    'Neither agree nor disagree': 0.5,
    'Agree': 0.75,
    'Strongly agree': 1,
    'Not at all worried': 0.1,
    'Not very worried': 0.3,
    'Fairly worried': 0.6,
    'Very worried': 0.9,
    'Poor': 0.2,
    'Fair': 0.4,
    'Good': 0.6,
    'Excellent': 0.8,
    'Very poor': 0.1,
    'Tend to agree': 0.6,
    'Strongly agree': 1,
    'Neither agree nor disagree': 0.5,
    'Tend to disagree': 0.4,
    'Fairly confident': 0.6,
    'Very confident': 0.8,
    'Not very confident': 0.3,
    'Not at all confident': 0.1,
    'Major problem': 0.8,
    'Minor problem': 0.5,
    'Not a problem at all': 0.2
}

weighted_questions = {'NNQ135A', 'NPQ135A', 'ReNQ147'}
