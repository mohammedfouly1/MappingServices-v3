# prompts.py
"""
Unified Prompts Module
Contains all prompt texts for different mapping types.
This replaces the separate .txt files (LabPrompt.txt, RadPrompt.txt, ServicePrompt.txt)
"""

class Prompts:
    """
    Container class for all mapping prompts.
    Access prompts using: Prompts.get("Lab"), Prompts.get("Radiology"), Prompts.get("Service")
    """
    
    # Laboratory Mapping Prompt
    LAB = """##Input You will receive 2 JSON Arrays: first JSON array is a table with two columns "First Group Code","First Group Name"; second JSON array is a table with two columns "Second Group Code","Second Group Name". ##Task Your task is to choose every Laboratory Examination "First Group Name" from the first group (you must output all first group Laboratory Examinations even there are no matching Laboratory Examinations from the second group), search and compare each Laboratory Examination against all services in the second group to select the most similar Laboratory Examination. Mapping must be based on word meaning and Laboratory Examination understanding, NOT keyword/string similarity. You MUST use medical knowledge to understand each test in deep detail including: technique (smear,culture,centrifuge,microscope,etc), approach (ELISA,immunofluorescence), substrate measured (IgM,IgG,cholesterol), organism (HBV,HIV,chlamydia,etc), level (direct/indirect/total bilirubin), specimen/anatomical site (blood,CSF,urine), test type (quantitative/qualitative), chemical state (free vs total), antigen vs antibodies. You must use knowledge examples (H. pylori in stool measures antigen; serum measures antibodies). Choose the most similar service name from the second group for each first group test considering aliases/abbreviations/synonyms/typos/punctuation and differences in technique/approach/substrate/organism/level/specimen/test type/chemical state/antigen-antibody. ##Strict constraints: You must NOT invent any codes or names. You must use exact terms (codes and names) exactly as they appear in FIRST_GROUP and SECOND_GROUP arrays. Output MUST be a JSON array only (no extra text, no markdown). ##Output format: Return a JSON array of objects. Each object MUST have exactly these 6 keys: 1) "First Group Code" 2) "First Group Name" 3) "Second Group Code" (use null only if truly no match exists in SECOND_GROUP) 4) "Second Group Name" (use null only if truly no match exists in SECOND_GROUP) 5) "Similarity Score" (integer 1–100; 1=least similar; 100=identical/near-identical) 6) "Score Reason" (short, medically specific reason). Scoring rules: "Similarity Score" must be integer 1–100 (never 0, never -1). If "Second Group Code" is null, "Similarity Score" MUST be exactly 5. If "Second Group Code" is not null, "Similarity Score" MUST be >= 30. No-match rule: Never output "no match" just because FIRST_GROUP item is underspecified/broader. If SECOND_GROUP contains a test in the same clinical concept, you MUST choose the closest and penalize the score accordingly. Use no-match ONLY when the clinical concept/test truly does not exist anywhere in SECOND_GROUP. Tie-break rules: A) Missing detail only (NOT conflicting): if FIRST_GROUP is missing a detail (e.g., "CBC without diff") but SECOND_GROUP has the same test with extra detail (CBC with diff), you MUST select it and score 80–95. B) Different method/specimen (same concept/analyte): if analyte/concept is same but method/specimen differs (e.g., UA dipstick vs UA microscopy; CRP vs hs-CRP), select closest and score 50–75 depending on severity. C) Profile/Panel vs Components: if FIRST_GROUP is a profile/panel and SECOND_GROUP contains only components, pick the component that best represents the panel core intent (not random), explain why, and score 50–70. Score calibration: Use 100 ONLY for identical/near-identical (synonym/abbreviation only). If any mismatch (method/specimen/detail/panel-vs-component), do NOT use 100. ======================================== Examples (NOT additional tasks; calibration only—do NOT include these examples in your output) Example output JSON array (3 items): [{"First Group Code":"FG-LAB-001","First Group Name":"CBC (بدون ذكر diff)","Second Group Code":"SG-LAB-101","Second Group Name":"Complete blood count (CBC) with automated differential","Similarity Score":90,"Score Reason":"Missing detail only: CBC without specifying differential still matches CBC with automated differential; differential is additional detail, not a conflict. High similarity but not identical."},{"First Group Code":"FG-LAB-012","First Group Name":"Urinalysis dipstick (UA) - بدون ميكروسكوب","Second Group Code":"SG-LAB-112","Second Group Name":"Urinalysis with microscopy","Similarity Score":65,"Score Reason":"Different method: dipstick UA vs microscopy UA. Same clinical concept (urinalysis) but microscopy adds/changes technique and findings depth. Moderate similarity."},{"First Group Code":"FG-LAB-020","First Group Name":"Iron profile (Iron/TIBC/Ferritin)","Second Group Code":"SG-LAB-121","Second Group Name":"Iron binding capacity, total (TIBC)","Similarity Score":60,"Score Reason":"Panel vs component: Iron profile is a panel; SECOND_GROUP offers components. TIBC best represents the panel core intent (binding capacity/iron status). Partial match only."""

    # Radiology Mapping Prompt
    RADIOLOGY = """ Act as a world-class Medical Data Analyst specializing in Radiology Mapping. Given the following context, criteria, and instructions,
                  ##Input You will receive 2 Json Arrays first json array are table with two column "First Group Code" , "First Group Name", second json array are second group are table with two column "Second Group Code" , "Second  Group Name". ##Task Your task is to choose every Radiological Examination from the first group, search and compare in each Radiological Examination in all services of the second group to select and choose the most similar Radiological Examination. You must output all first group Radiological Examinations, even if there are no matching Radiological Examinations in the second group. Your mapping should be based on medical knowledge, word meaning, and understanding of each Radiological Examination's details. ## Context Your mapping should be based on word meaning and understanding of each Radiological Examination's details, including anatomical site, use of contrast, purpose of the examination, patient preparation, invasiveness and patient comfort, equipment and technology used, image review and reporting, radiation dose, patient positioning and mobility requirements, ability to image moving organs, contrast medium type and administration route, and Radiology-specific discriminators  as : Modality: XR / US / CT / MRI / NM / PET-CT / Fluoroscopy / Mammography. Anatomy + sub-anatomy: e.g., “Brain” vs “Pituitary” vs “IAC”; “Chest” vs “CTA Pulmonary”. Laterality: left/right, bilateral. Contrast: none / with IV contrast / without contrast / with & without / oral contrast / rectal contrast / intrathecal contrast. Protocol/intent: routine vs trauma vs oncology staging vs angiography vs perfusion vs urography. Functional vs structural: Doppler vs non-Doppler US; MR spectroscopy; perfusion CT/MRI. Phase/timing: arterial/venous/delayed; multiphase liver; dynamic contrast. Technique: with sedation, portable, weight-bearing, standing, prone/supine, 3D recon, low-dose. Composite exams: “Abdomen/Pelvis”, “Head/Neck”, “Spine whole”, “Brain + IAC”. Interventional vs diagnostic: biopsy/drainage/angiography vs diagnostic imaging. Radiology “distractors” as : Contrast variants: “w contrast”, “without”, “w/wo” , CTA vs CTV vs MRA vs MRV , “CT Chest” vs “CTPA” (pulmonary angiography) , MRI sequences: “DWI”, “FLAIR”, “SWI” (if present), Laterality: “MRI Knee Left” vs “MRI Knee Right” , Region scope: “Lumbar spine” vs “whole spine” , Different purpose: “Screening mammography” vs “diagnostic mammography” , Portable vs department X-ray , This is what makes the benchmark meaningful and prevents models from “getting lucky” via string similarity. ##Strict constraints: - You must NOT invent any codes or names. - You must use the exact terms (codes and names) exactly as they appear in the provided FIRST_GROUP and SECOND_GROUP arrays. - Output MUST be a JSON array only (no extra text, no markdown). ##Output format: your response  must return a JSON array of objects, Each object MUST have exactly these 6 keys (and in this meaning): 1) "First Group Code" 2) "First Group Name" 3) "Second Group Code"     (use null only if truly no match exists in SECOND_GROUP) 4) "Second Group Name"     (use null only if truly no match exists in SECOND_GROUP) 5) "Similarity Score"        your judgment as a score for degree of similarity, score 1 (less similarity) to 100 (identical or near identical similarity)(integer 1–100 only) 6) "Score Reason"          (short but medically specific reason for the chosen score)
                  Scoring rules : - "Similarity Score" must be an integer 1–100 (never 0, never -1). - If "Second Group Code" is null (no match), then "Similarity Score" MUST be exactly 5. - If "Second Group Code" is not null (a match chosen), then "Similarity Score" MUST be >= 30.
                  No-match rule : - Never output “no match” just because the FIRST_GROUP item is underspecified or broader. - If SECOND_GROUP contains a radiological test in the same clinical concept, you MUST choose the closest one and penalize the score accordingly. - Use no-match ONLY when the clinical concept/test truly does not exist anywhere in SECOND_GROUP.
                  ## Instructions - Choose every Radiological Examination from the first group, even if there are no matching ones from the second group - Search and compare each Radiological Examination in the second group to select and choose the most similar Radiological Examination - Strictly adhere to the exact terms provided in both the first and second groups - Use your medical knowledge to understand and compare each Radiological Examination's details - Provide a judgment score for the degree of similarity, along with a reason for the similarity score
                  when the radiological examination type is completely absent ( not complete name or abbreviation ) , so it xray 
                  when no other radiological examination type is mentioned , and names have (one view , two views ),  so it xray .
                  The term (radiograph) is exactly another anime for the same as Xray."""

    # Service Mapping Prompt
    SERVICE = """-Act as a world-class Medical Data Analyst specializing in Medical Services Names Mapping. Given the following context, criteria, and instructions,
##Input
You will receive 2 Json Arrays first json array are table with two column "First Group Code" , "First Group Name", second json array are second group are table with two column "Second Group Code" , "Second  Group Name".
##Task
Your task is to choose every Medical Service from the first group, search and compare each Medical Service in all Items of the second group to select and choose the most similar Medical Service.
Your mapping should be based on medical knowledge, word meaning, and understanding of each Medical Service Name details.
Your mapping should be based on word meaning and understanding of each Service Name details , every service as a structured object, not just text. You must clearly understand the highest-value dimensions for correct mapping as :
A) Service family / domain (hard filter) as : ENT (ear wash, nasal cautery, turbinate procedures) , Ortho (splints, casts, spica) , Ophthalmology (lashes epilation, contact lenses, plugs) , Cardio/Diagnostics (ECG/EKG) , Neurophysiology (VEP/BAER/EEG/EMG) , Lab/Serology/Pathology (IgG/IgM, TORCH, complement fixation, biopsy/culture).
B) Clinical “action” type (procedure vs test vs supply vs interpretation) as : Procedure (e.g., male circumcision) , Diagnostic test (e.g., Tone decay test, VEP) , Supply/device (e.g., finger splint single-use) , Interpretation/report only (e.g., “Interpretation of Bone Marrow smear”).
C) Anatomy + sub-anatomy (and body system) as : Ear vs nose vs turbinate (ENT) , Hand/finger vs hip (Ortho) , Bone marrow (Heme/Path) , CNS evoked potentials (Neuro).
D) Laterality (unilateral / bilateral / left / right)as : “Fitting/testing of hearing aid, unilateral” vs “…bilateral” , “Visual evoked potential [VEP], unilateral” , “Submucous resection of turbinate, unilateral” , “Hip spica, unilateral/bilateral”.
E) Technique / modality / method (often the main discriminator) as : Complement fixation method (lab) vs generic “antibody test” , “Suction under microscope” vs routine suction , “Evoked response audiometry” vs “visual evoked potential”.
F) Specimen / material / sample type (lab + some procedures) as : Serum/plasma/CSF/tissue/culture specimen types, etc. , (Even if not always written in your local names, NPHIES often implies it.).
G) Quantifiers (size, extent, duration, units, percentages) as : Very important for dressings/casts/monitoring:, Burn dressing: small/medium/large + % BSA thresholds , Monitoring: “pulmonary function monitoring for >= 6 hours” , Splints/casts: type + sometimes single-use.
H) Intent / context (screening vs diagnostic vs therapeutic) as :“TORCH screening” vs single antibody, measurement, Diagnostic thoracentesis vs therapeutic drainage (if present).
I) Anesthesia / sedation / approach (OPD-level discriminator) as : “Circumcision under L.A.” , Polypectomy under LA, etc.
J) Granularity level (broad vs specific) as : Local service is vague → map to “unspecified/other/unlisted” only if anatomy+family still align. , Local service is specific → never map to a broader code if a specific match exists.
You must have clear knowledge with points that cause Distractors in mapping of Medical Service names as :
1) Same word-root, different procedure category (VERY dangerous) as : Gastroscopy (endoscopy) , and Gastrotomy (surgical incision) , as Same “gastro-”, totally different action + invasiveness + approach.
2) Procedure vs interpretation/report-only as : Bone marrow biopsy , and Interpretation of Bone Marrow smear , as Biopsy ≠ smear interpretation. “Bone marrow” alone is not enough.
3) “Test” vs “monitoring for duration” as : Pulmonary function test , and Continuous monitoring of pulmonary function for >=6 hours , as Duration qualifier changes the service into a different category.
4) Laterality mismatch as : “Visual evoked response” (no laterality stated) , and “VEP, unilateral” If laterality is missing locally,
5) Range/threshold mismatches (burn dressing example) as : Local uses thresholds like “>25% / 5–25% / <5%”, , and describes “>=10% / 5–10% / <5%”. , as the same label (large/medium/small) but different definitions. Needs explicit “range logic”.
6) Abbreviations that are ambiguous across specialties as :PRP in ophthalmology (panretinal photocoagulation) , and PRP in other contexts (platelet-rich plasma). , as EKG/ECG same meaning, but model might treat as different unless normalized.
7) Mixed language + spelling noise as : Arabic/English mixtures and typos (e.g., “LANSER” vs “LASER”) create false negatives unless normalized.
8) Supply/device vs procedure as : “Large finger/toe splint”, and “Hand/finger splint, single-use” , as Sometimes describes the device, describes device class; you must detect “device/supply”.
##Strict constraints:
- You must NOT invent any codes or names.
- You must use the exact terms (codes and names) exactly as they appear in the provided FIRST_GROUP and SECOND_GROUP arrays.
- Output MUST be a JSON array only (no extra text, no markdown).
##Output format:
your response must return a JSON array of objects, Each object MUST have exactly these 6 keys (and in this meaning):
1) "First Group Code"
2) "First Group Name"
3) "Second Group Code"     (use null only if truly no match exists in SECOND_GROUP)
4) "Second Group Name"     (use null only if truly no match exists in SECOND_GROUP)
5) "Similarity Score"        your judgment as a score for degree of similarity, score 1 (less similarity) to 100 (identical or near identical similarity)(integer 1–100 only)
6) "Score Reason"          (short but medically specific reason for the chosen score)
Scoring rules :
- "Similarity Score" must be an integer 1–100 (never 0, never -1).
- If "Second Group Code" is null (no match), then "Similarity Score" MUST be exactly 5.
        - If "Second Group Code" is not null (a match chosen), then "Similarity Score" MUST be >= 30.
         No-match rule :
        - Never output “no match” just because the FIRST_GROUP item is underspecified or broader.
        - If SECOND_GROUP contains a test in the same clinical concept, you MUST choose the closest one and penalize the score accordingly.
        - Use no-match ONLY when the clinical concept/test truly does not exist anywhere in SECOND_GROUP."""


    # Mapping dictionary for easy access
    _PROMPTS = {
        "Lab": LAB,
        "lab": LAB,
        "LAB": LAB,
        "laboratory": LAB,
        "Laboratory": LAB,
        "Radiology": RADIOLOGY,
        "radiology": RADIOLOGY,
        "RADIOLOGY": RADIOLOGY,
        "Rad": RADIOLOGY,
        "rad": RADIOLOGY,
        "Service": SERVICE,
        "service": SERVICE,
        "SERVICE": SERVICE,
    }
    
    @classmethod
    def get(cls, prompt_type: str) -> str:
        """
        Get prompt text by type.
        
        Args:
            prompt_type: One of "Lab", "Radiology", or "Service" (case-insensitive)
        
        Returns:
            The prompt text string
        
        Raises:
            ValueError: If prompt_type is not recognized
        
        Examples:
            >>> prompt = Prompts.get("Lab")
            >>> prompt = Prompts.get("Radiology")
            >>> prompt = Prompts.get("Service")
        """
        prompt = cls._PROMPTS.get(prompt_type)
        if prompt is None:
            available = ["Lab", "Radiology", "Service"]
            raise ValueError(f"Unknown prompt type: '{prompt_type}'. Available types: {available}")
        return prompt
    
    @classmethod
    def get_all_types(cls) -> list:
        """
        Get list of available prompt types.
        
        Returns:
            List of prompt type names
        """
        return ["Lab", "Radiology", "Service"]
    
    @classmethod
    def get_prompt_info(cls, prompt_type: str) -> dict:
        """
        Get prompt information including metadata.
        
        Args:
            prompt_type: One of "Lab", "Radiology", or "Service"
        
        Returns:
            Dictionary with prompt text and metadata
        """
        prompt_text = cls.get(prompt_type)
        
        info = {
            "Lab": {
                "name": "Laboratory Mapping",
                "icon": "🧪",
                "description": "Maps laboratory test items based on medical knowledge",
                "focus_areas": [
                    "technique (smear, culture, centrifuge, microscope)",
                    "approach (ELISA, immunofluorescence)",
                    "substrate measured (IGM, IGG, Cholesterol)",
                    "organism (hepatitis b, hiv, chlamydia)",
                    "anatomical site (blood, CSF, urine)",
                    "test type (quantitative or qualitative)"
                ]
            },
            "Radiology": {
                "name": "Radiology Mapping",
                "icon": "📷",
                "description": "Maps radiological examinations based on imaging details",
                "focus_areas": [
                    "anatomical site",
                    "use of contrast",
                    "equipment and technology",
                    "radiation dose",
                    "patient positioning",
                    "contrast medium type"
                ]
            },
            "Service": {
                "name": "Medical Service Mapping",
                "icon": "🔧",
                "description": "Maps general medical services",
                "focus_areas": [
                    "service type",
                    "procedure details",
                    "equipment used",
                    "patient preparation",
                    "invasiveness level"
                ]
            }
        }
        
        result = info.get(prompt_type, {})
        result["text"] = prompt_text
        result["length"] = len(prompt_text)
        
        return result


# Convenience function for backward compatibility
def get_prompt(prompt_type: str) -> str:
    """
    Convenience function to get prompt text.
    This maintains compatibility with code that might call get_prompt() directly.
    
    Args:
        prompt_type: One of "Lab", "Radiology", or "Service"
    
    Returns:
        The prompt text string
    """
    return Prompts.get(prompt_type)


# For testing
if __name__ == "__main__":
    print("Available prompt types:", Prompts.get_all_types())
    print("\n" + "="*50)
    
    for ptype in Prompts.get_all_types():
        info = Prompts.get_prompt_info(ptype)
        print(f"\n{info['icon']} {info['name']}")
        print(f"   Description: {info['description']}")
        print(f"   Length: {info['length']} characters")
        print(f"   Focus areas: {', '.join(info['focus_areas'][:3])}...")