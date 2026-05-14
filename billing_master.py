"""
billing_master.py — Master billing item registry by therapeutic area.

This is the institutional knowledge layer that makes the agent work.
Raw Claude cannot know your site's standard billing items — this file
encodes them. The agent loads the relevant section based on study type
and diffs it against the contract. Sponsors routinely omit 3-7 items
per contract; each omission is recoverable revenue.

To extend: add a new therapeutic area key with its standard item list.
"""

STUDY_CATEGORIES = {
    "Oncology": "Cancer / tumor / hematology studies",
    "Pulmonology": "Lung / respiratory / COPD / asthma studies",
    "Cardiology": "Cardiovascular / heart failure / lipid studies",
    "Neurology": "CNS / Alzheimer's / Parkinson's / MS studies",
    "Infectious Disease": "Antiviral / antibiotic / vaccine studies",
    "Endocrinology": "Diabetes / thyroid / metabolic studies",
    "Rheumatology": "Autoimmune / arthritis / lupus studies",
    "Dermatology": "Skin / psoriasis / eczema studies",
}

BILLING_MASTER = {

    "Oncology": [
        {
            "name": "Screen Failure Fee",
            "category": "Patient Procedures",
            "typical_rate": 850,
            "unit": "occurrence",
            "rationale": "Sponsors cap or omit screen failure fees in oncology despite high screening costs from labs, biopsies, and imaging required to establish eligibility.",
            "suggested_language": "Site shall be reimbursed $850 per screen failure, defined as any patient who completes screening procedures but does not meet eligibility criteria, regardless of reason for failure."
        },
        {
            "name": "Tumor Biopsy Processing Fee",
            "category": "Laboratory",
            "typical_rate": 1200,
            "unit": "sample",
            "rationale": "Fresh tumor biopsies require specialized handling, storage at -80°C, and chain-of-custody documentation. Sponsors bundle this into visit fees at rates that do not cover actual cost.",
            "suggested_language": "Tumor biopsy processing, including fresh tissue handling, storage, and shipment, shall be reimbursed at $1,200 per sample, separate from visit fees."
        },
        {
            "name": "Serious Adverse Event (SAE) Reporting Fee",
            "category": "Safety Reporting",
            "typical_rate": 500,
            "unit": "event",
            "rationale": "SAE reporting in oncology requires physician narrative, source documentation, and expedited submission within 24 hours. This labor cost is rarely compensated.",
            "suggested_language": "Site shall receive $500 per SAE report submitted, covering investigator narrative preparation, medical record compilation, and regulatory submission."
        },
        {
            "name": "Unscheduled Visit Fee",
            "category": "Patient Procedures",
            "typical_rate": 600,
            "unit": "visit",
            "rationale": "Oncology patients frequently require unscheduled visits for toxicity management. Sponsors omit this or bundle it into per-patient stipends.",
            "suggested_language": "Unscheduled visits necessitated by protocol-related adverse events shall be reimbursed at $600 per visit."
        },
        {
            "name": "Pharmacy Preparation Fee",
            "category": "Drug Handling",
            "typical_rate": 350,
            "unit": "preparation",
            "rationale": "IV chemotherapy and investigational biologics require pharmacist preparation under sterile conditions. This is separate from drug cost and often omitted.",
            "suggested_language": "Pharmacy preparation of investigational product, including sterile compounding and quality check, shall be reimbursed at $350 per preparation."
        },
        {
            "name": "Regulatory Document Fee",
            "category": "Administration",
            "typical_rate": 2500,
            "unit": "study startup",
            "rationale": "IRB submissions, protocol amendments, and regulatory binder maintenance represent 20-40 hours of coordinator time. Sponsors routinely omit a startup administration fee.",
            "suggested_language": "A one-time regulatory startup fee of $2,500 shall be paid upon site activation, covering IRB submission, regulatory binder preparation, and protocol review."
        },
        {
            "name": "Long-Term Follow-Up Visit",
            "category": "Patient Procedures",
            "typical_rate": 400,
            "unit": "visit",
            "rationale": "Oncology protocols often include 1-5 year follow-up periods. These visits are frequently omitted from the budget or priced below cost.",
            "suggested_language": "Long-term follow-up visits occurring after end of treatment shall be reimbursed at $400 per visit."
        },
    ],

    "Pulmonology": [
        {
            "name": "Spirometry Administration Fee",
            "category": "Pulmonary Function Testing",
            "typical_rate": 275,
            "unit": "test",
            "rationale": "Pulmonology trials require multiple spirometry tests per visit with certified technician time. Sponsors bundle this into visit fees at rates below cost.",
            "suggested_language": "Spirometry testing, including technician time, calibration, and quality control review, shall be reimbursed at $275 per test session."
        },
        {
            "name": "Screen Failure Fee",
            "category": "Patient Procedures",
            "typical_rate": 650,
            "unit": "occurrence",
            "rationale": "Pulmonology trials have high screen failure rates due to reversibility criteria. Screening requires spirometry, chest imaging, and laboratory work.",
            "suggested_language": "Site shall be reimbursed $650 per screen failure for patients who complete all screening procedures but do not meet eligibility criteria."
        },
        {
            "name": "Induced Sputum Processing Fee",
            "category": "Laboratory",
            "typical_rate": 400,
            "unit": "sample",
            "rationale": "Sputum induction requires nebulizer equipment, respiratory therapist time, and cytospin processing. Often omitted or merged with visit fees.",
            "suggested_language": "Induced sputum collection and cytospin processing shall be reimbursed at $400 per sample, separate from visit fees."
        },
        {
            "name": "Rescue Medication Dispensing Fee",
            "category": "Drug Handling",
            "typical_rate": 150,
            "unit": "dispensing event",
            "rationale": "COPD and asthma trials require tracking and dispensing rescue inhalers. This coordinator and pharmacy time is commonly absent from budgets.",
            "suggested_language": "Rescue medication dispensing and accountability documentation shall be reimbursed at $150 per dispensing event."
        },
        {
            "name": "FeNO (Fractional Exhaled Nitric Oxide) Testing Fee",
            "category": "Pulmonary Function Testing",
            "typical_rate": 200,
            "unit": "test",
            "rationale": "FeNO is standard in asthma/eosinophilic trials but equipment cost and technician time are rarely reimbursed separately.",
            "suggested_language": "FeNO measurement shall be reimbursed at $200 per test, inclusive of equipment calibration and technician administration."
        },
        {
            "name": "SAE Reporting Fee",
            "category": "Safety Reporting",
            "typical_rate": 450,
            "unit": "event",
            "rationale": "Exacerbations in pulmonology trials often qualify as SAEs requiring expedited reporting. Reporting labor is rarely compensated.",
            "suggested_language": "Site shall receive $450 per SAE report submitted, covering investigator narrative and regulatory submission within required timelines."
        },
        {
            "name": "Regulatory Document Fee",
            "category": "Administration",
            "typical_rate": 2000,
            "unit": "study startup",
            "rationale": "IRB submissions and protocol setup require significant administrative time routinely absent from pulmonology budgets.",
            "suggested_language": "A one-time regulatory startup fee of $2,000 shall be paid upon site activation."
        },
    ],

    "Cardiology": [
        {
            "name": "ECG Interpretation Fee",
            "category": "Cardiac Procedures",
            "typical_rate": 125,
            "unit": "ECG",
            "rationale": "Cardiology trials require serial ECGs with cardiologist interpretation. Sponsors price ECGs at equipment cost only, excluding physician reading time.",
            "suggested_language": "12-lead ECG including cardiologist interpretation shall be reimbursed at $125 per ECG."
        },
        {
            "name": "Screen Failure Fee",
            "category": "Patient Procedures",
            "typical_rate": 750,
            "unit": "occurrence",
            "rationale": "Cardiac eligibility criteria require stress testing, echocardiography, and extensive lab panels, making screen failure cost significant.",
            "suggested_language": "Site shall be reimbursed $750 per screen failure for patients completing all cardiac screening procedures."
        },
        {
            "name": "Holter Monitor Administration Fee",
            "category": "Cardiac Procedures",
            "typical_rate": 300,
            "unit": "monitoring period",
            "rationale": "Holter application, patient education, retrieval, and data download require coordinator and technician time not captured in visit fees.",
            "suggested_language": "Holter monitor application, retrieval, and data download shall be reimbursed at $300 per monitoring period."
        },
        {
            "name": "Echocardiogram Coordination Fee",
            "category": "Cardiac Procedures",
            "typical_rate": 200,
            "unit": "study",
            "rationale": "Scheduling, coordinating, and transmitting echo data to core labs requires site coordinator time beyond the echo reading fee.",
            "suggested_language": "Echo coordination including scheduling, quality check, and core lab transmission shall be reimbursed at $200 per study."
        },
        {
            "name": "SAE Reporting Fee",
            "category": "Safety Reporting",
            "typical_rate": 550,
            "unit": "event",
            "rationale": "Cardiac SAEs (MI, arrhythmia, heart failure hospitalization) require complex narrative and source documentation.",
            "suggested_language": "Site shall receive $550 per cardiac SAE report, covering physician narrative, source documentation, and submission."
        },
        {
            "name": "Regulatory Document Fee",
            "category": "Administration",
            "typical_rate": 2200,
            "unit": "study startup",
            "rationale": "Cardiology trials often require device certifications and additional regulatory submissions beyond standard IRB.",
            "suggested_language": "A one-time regulatory startup fee of $2,200 shall be paid upon site activation."
        },
    ],

    "Neurology": [
        {
            "name": "Cognitive Assessment Administration Fee",
            "category": "Neurological Assessments",
            "typical_rate": 450,
            "unit": "assessment",
            "rationale": "MMSE, MoCA, ADAS-Cog, and other cognitive batteries require 45-90 minutes of trained rater time. Sponsors undervalue this in visit fees.",
            "suggested_language": "Standardized cognitive assessments (MMSE, MoCA, ADAS-Cog, or equivalent) shall be reimbursed at $450 per assessment, inclusive of rater time and scoring."
        },
        {
            "name": "Screen Failure Fee",
            "category": "Patient Procedures",
            "typical_rate": 900,
            "unit": "occurrence",
            "rationale": "Neurology screening involves neuropsychological testing, MRI, and PET scans. Screen failure cost is among the highest of any therapeutic area.",
            "suggested_language": "Site shall be reimbursed $900 per screen failure for patients completing neurological screening procedures."
        },
        {
            "name": "Lumbar Puncture Procedure Fee",
            "category": "Procedures",
            "typical_rate": 1500,
            "unit": "procedure",
            "rationale": "CSF collection requires physician time, sterile setup, patient monitoring, and post-procedure observation. Sponsors frequently underprice this procedure.",
            "suggested_language": "Lumbar puncture including physician time, sterile supplies, CSF processing, and post-procedure monitoring shall be reimbursed at $1,500 per procedure."
        },
        {
            "name": "Caregiver Reimbursement",
            "category": "Patient Support",
            "typical_rate": 150,
            "unit": "visit",
            "rationale": "Alzheimer's and dementia trials require caregiver presence. Travel and time reimbursement for caregivers is often omitted.",
            "suggested_language": "Caregiver travel and time reimbursement shall be provided at $150 per study visit requiring caregiver attendance."
        },
        {
            "name": "SAE Reporting Fee",
            "category": "Safety Reporting",
            "typical_rate": 500,
            "unit": "event",
            "rationale": "Neurological SAEs (seizures, strokes, falls with injury) require detailed physician narrative and source documentation.",
            "suggested_language": "Site shall receive $500 per SAE report submitted for neurological events."
        },
        {
            "name": "Regulatory Document Fee",
            "category": "Administration",
            "typical_rate": 2500,
            "unit": "study startup",
            "rationale": "Neurology trials frequently involve additional regulatory complexity including device components and genetics consents.",
            "suggested_language": "A one-time regulatory startup fee of $2,500 shall be paid upon site activation."
        },
    ],

    "Infectious Disease": [
        {
            "name": "Screen Failure Fee",
            "category": "Patient Procedures",
            "typical_rate": 500,
            "unit": "occurrence",
            "rationale": "ID trials often have rapid enrollment windows with high screen failure rates, particularly in viral studies requiring active infection confirmation.",
            "suggested_language": "Site shall be reimbursed $500 per screen failure for patients completing all screening procedures."
        },
        {
            "name": "Virology Sample Processing Fee",
            "category": "Laboratory",
            "typical_rate": 350,
            "unit": "sample",
            "rationale": "Viral load testing, resistance genotyping, and serological assays require BSL-2 handling and specialized processing not captured in standard lab fees.",
            "suggested_language": "Virology sample processing including viral load quantification and genotyping shall be reimbursed at $350 per sample set."
        },
        {
            "name": "Isolation Protocol Compliance Fee",
            "category": "Patient Procedures",
            "typical_rate": 250,
            "unit": "visit",
            "rationale": "Infectious disease trials require PPE, isolation rooms, and enhanced cleaning between patients. This overhead is rarely reimbursed.",
            "suggested_language": "Infection control compliance costs including PPE and isolation room use shall be reimbursed at $250 per patient visit."
        },
        {
            "name": "SAE Reporting Fee",
            "category": "Safety Reporting",
            "typical_rate": 450,
            "unit": "event",
            "rationale": "SAEs in ID trials often require public health notifications in addition to sponsor reporting.",
            "suggested_language": "Site shall receive $450 per SAE report submitted."
        },
        {
            "name": "Regulatory Document Fee",
            "category": "Administration",
            "typical_rate": 1800,
            "unit": "study startup",
            "rationale": "ID trials often require biohazard certifications and additional institutional approvals.",
            "suggested_language": "A one-time regulatory startup fee of $1,800 shall be paid upon site activation."
        },
    ],

    "Endocrinology": [
        {
            "name": "Screen Failure Fee",
            "category": "Patient Procedures",
            "typical_rate": 600,
            "unit": "occurrence",
            "rationale": "Diabetes trials require HbA1c, fasting glucose, and renal function panels to confirm eligibility. Screen failure cost is significant.",
            "suggested_language": "Site shall be reimbursed $600 per screen failure for patients completing endocrinology screening procedures."
        },
        {
            "name": "Continuous Glucose Monitor (CGM) Setup Fee",
            "category": "Device Procedures",
            "typical_rate": 300,
            "unit": "setup",
            "rationale": "CGM application, patient training, and data download require coordinator time absent from standard visit fees.",
            "suggested_language": "CGM device setup, patient training, and data download shall be reimbursed at $300 per setup event."
        },
        {
            "name": "OGTT Administration Fee",
            "category": "Metabolic Testing",
            "typical_rate": 200,
            "unit": "test",
            "rationale": "Oral glucose tolerance testing requires 2-hour patient monitoring and serial blood draws. This extended chair time is undercompensated.",
            "suggested_language": "OGTT including glucose preparation, serial sampling, and 2-hour patient monitoring shall be reimbursed at $200 per test."
        },
        {
            "name": "SAE Reporting Fee",
            "category": "Safety Reporting",
            "typical_rate": 450,
            "unit": "event",
            "rationale": "Hypoglycemic SAEs require detailed narrative and often emergency documentation.",
            "suggested_language": "Site shall receive $450 per SAE report submitted."
        },
        {
            "name": "Regulatory Document Fee",
            "category": "Administration",
            "typical_rate": 2000,
            "unit": "study startup",
            "rationale": "Endocrinology trials frequently involve device components requiring additional regulatory submissions.",
            "suggested_language": "A one-time regulatory startup fee of $2,000 shall be paid upon site activation."
        },
    ],

    "Rheumatology": [
        {
            "name": "Screen Failure Fee",
            "category": "Patient Procedures",
            "typical_rate": 700,
            "unit": "occurrence",
            "rationale": "Autoimmune trials require extensive lab panels including ANA, anti-dsDNA, complement levels, and TB testing. Screen failure costs are high.",
            "suggested_language": "Site shall be reimbursed $700 per screen failure for patients completing rheumatology screening procedures."
        },
        {
            "name": "Joint Assessment Administration Fee",
            "category": "Clinical Assessments",
            "typical_rate": 350,
            "unit": "assessment",
            "rationale": "Formal 28-joint or 68/66-joint counts require trained assessor time not captured in standard visit fees.",
            "suggested_language": "Formal joint assessment (28-joint count or 68/66-joint count) shall be reimbursed at $350 per assessment."
        },
        {
            "name": "Infusion Suite Fee",
            "category": "Drug Administration",
            "typical_rate": 500,
            "unit": "infusion",
            "rationale": "Biologic infusions require nursing time, infusion chair, vital sign monitoring, and 30-60 minute post-infusion observation.",
            "suggested_language": "Infusion suite use including nursing administration and post-infusion monitoring shall be reimbursed at $500 per infusion."
        },
        {
            "name": "SAE Reporting Fee",
            "category": "Safety Reporting",
            "typical_rate": 500,
            "unit": "event",
            "rationale": "Serious infections and malignancies in immunosuppressed patients require complex SAE narratives.",
            "suggested_language": "Site shall receive $500 per SAE report submitted."
        },
        {
            "name": "Regulatory Document Fee",
            "category": "Administration",
            "typical_rate": 2200,
            "unit": "study startup",
            "rationale": "Rheumatology trials often require TB and hepatitis screening certifications and additional biosafety documentation.",
            "suggested_language": "A one-time regulatory startup fee of $2,200 shall be paid upon site activation."
        },
    ],

    "Dermatology": [
        {
            "name": "Screen Failure Fee",
            "category": "Patient Procedures",
            "typical_rate": 550,
            "unit": "occurrence",
            "rationale": "Dermatology trials require PASI/IGA scoring and photography at screening. Screen failure cost is often not reimbursed.",
            "suggested_language": "Site shall be reimbursed $550 per screen failure for patients completing dermatology screening procedures."
        },
        {
            "name": "Standardized Photography Fee",
            "category": "Clinical Assessments",
            "typical_rate": 175,
            "unit": "session",
            "rationale": "Standardized clinical photography requires controlled lighting, positioning, and storage protocols. Equipment and time cost is routinely omitted.",
            "suggested_language": "Standardized clinical photography sessions shall be reimbursed at $175 per session."
        },
        {
            "name": "Skin Biopsy Processing Fee",
            "category": "Laboratory",
            "typical_rate": 600,
            "unit": "biopsy",
            "rationale": "Punch biopsies require physician time, histology processing, and often immunohistochemistry staining. Sponsors bundle this at below-cost rates.",
            "suggested_language": "Skin biopsy including punch procedure, histology processing, and IHC staining shall be reimbursed at $600 per biopsy."
        },
        {
            "name": "PASI/IGA Assessment Fee",
            "category": "Clinical Assessments",
            "typical_rate": 200,
            "unit": "assessment",
            "rationale": "Psoriasis Area Severity Index scoring requires trained assessor time and is commonly undercompensated in visit fees.",
            "suggested_language": "PASI and IGA assessments shall be reimbursed at $200 per assessment session."
        },
        {
            "name": "SAE Reporting Fee",
            "category": "Safety Reporting",
            "typical_rate": 400,
            "unit": "event",
            "rationale": "Serious skin reactions (SJS, TEN) require urgent detailed documentation.",
            "suggested_language": "Site shall receive $400 per SAE report submitted."
        },
        {
            "name": "Regulatory Document Fee",
            "category": "Administration",
            "typical_rate": 1800,
            "unit": "study startup",
            "rationale": "Standard regulatory startup costs are routinely absent from dermatology budgets.",
            "suggested_language": "A one-time regulatory startup fee of $1,800 shall be paid upon site activation."
        },
    ],
}
