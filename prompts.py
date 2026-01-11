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
    LAB = """You will receive 2 Json Arrays  first json array are table with two column "First Group Code" , "First Group Name", second json array are  second group are table with two column "Second Group Code" , "Second  Group Name" .
Your task is to choose every Laboratory Examinations "First Group Name"   from the first group (you must output all first group Laboratory Examinations even there are no matching Laboratory Examinations from the second group ) , search and compare in each Laboratory Examinations in all services of the second group to select and choose the most similar Laboratory Examination . 
Mapping should be based on word meaning and Laboratory Examination service name understanding and Not depend on keyword or string similarity, and should use your medical knowledge to understand each Laboratory Examination details, , with a deep and detailed understanding including: technique(smear, culture , centrifuge , or microscope, etc), , approach (by Elisa , immunofluorescence) , substrate measured (IGM, IGG, Cholesterol) , if organism included (hepatitis b, hiv, chlamydia, etc) , substrate level (direct and indirect and total bilirubin) , anatomical site of sample (blood,CSF, urine), test type (quantitative or qualitative), chemical state of substance measured (free t3 (unbound) or total t3) , antigen or antibodies. you should use your information( as h.pylori in stool measure organism antigen , while h.pylori in serum measure organism antibodies), should use your medical knowledge to understand each test's details. and choose the most similar service name from the second group for medical laboratory test from the first group (as other alias, name,abbreviation , synonyms , typing errors or punctuations )to each other, or different technique,approach, substrate measured, organism included , substrate measured , substrate level , anatomical site of sample,test type,chemical state of substance measured ,antigen or antibodies. 
your output must strictly adhere to the exact terms provided in both the first and second groups.
 your response should be in jason array with each item have 6 columns , first column have First Group Code from the first group , second column have First Group Name  from the first group ,Third column have Second Group Code chosen from the second group , Fourth column have Second  Group Name chosen from the second group you must output all first group Laboratory Examination even there are no matching Laboratory Examination from the second group ) , Fifth column have your judgment as score for degree of similarity, score 1 (less similarity) to 100 (identical or near identical similarity), Sixth Column should have reason for similarity score."""

    # Radiology Mapping Prompt
    RADIOLOGY = """Act as a world-class Medical Data Analyst specializing in Radiology Mapping. Given the following context, criteria, and instructions, your task is to choose every Radiological Examination from the first group, search and compare in each Radiological Examination in all services of the second group to select and choose the most similar Radiological Examination. ## Context You will receive two tables. The first group contains two columns: "Service Code" and "Service Description." The second group also contains two columns: "SBS Code" and "SBS Description." Your mapping should be based on word meaning and understanding of each Radiological Examination's details, including anatomical site, use of contrast, purpose of the examination, patient preparation, invasiveness and patient comfort, equipment and technology used, image review and reporting, radiation dose, patient positioning and mobility requirements, ability to image moving organs, contrast medium type and administration route. ## Approach You must output all first group Radiological Examinations, even if there are no matching Radiological Examinations in the second group. Your mapping should be based on medical knowledge, word meaning, and understanding of each Radiological Examination's details as outlined in the context. ## Response Format Your response should be in a tabular structure with six columns: 1. Service code from the first group 2. Service name from the first group 3. Service code chosen from the second group 4. Service name chosen from the second group 5. Judgment as score for degree of similarity (1 for less similarity to 100 for identical or near-identical similarity) 6. Reason for similarity score ## Instructions - Choose every Radiological Examination from the first group, even if there are no matching ones from the second group - Search and compare each Radiological Examination in the second group to select and choose the most similar Radiological Examination - Strictly adhere to the exact terms provided in both the first and second groups - Use your medical knowledge to understand and compare each Radiological Examination's details - Provide a judgment score for the degree of similarity, along with a reason for the similarity score"""

    # Service Mapping Prompt
    SERVICE = """Act as a world-class Medical Data Analyst specializing in Medical Services Mapping. Given the following context, criteria, and instructions, your task is to choose every Medical Service Name from the first group, search and compare in each Medical Service Name in all services of the second group to select and choose the most similar Medical Service Name. ## Context You will receive two tables. The first group contains two columns: "Service Code" and "Service Description." The second group also contains two columns: "SBS Code" and "SBS Description." Your mapping should be based on word meaning and understanding of each Medical Service Name details, including anatomical site, use of contrast, purpose of the examination, patient preparation, invasiveness and patient comfort, equipment and technology used, image review and reporting, radiation dose, patient positioning and mobility requirements, ability to image moving organs, contrast medium type and administration route. ## Approach You must output all first group Medical Service Name, even if there are no matching Medical Service Name in the second group. Your mapping should be based on medical knowledge, word meaning, and understanding of each Medical Service Name details as outlined in the context. ## Response Format Your response should be in a tabular structure with six columns: 1. Service code from the first group 2. Service name from the first group 3. Service code chosen from the second group 4. Service name chosen from the second group 5. Judgment as score for degree of similarity (1 for less similarity to 100 for identical or near-identical similarity) 6. Reason for similarity score ## Instructions - Choose every Medical Service Name from the first group, even if there are no matching ones from the second group - Search and compare each Medical Service Name in the second group to select and choose the most similar Medical Service Name - Strictly adhere to the exact terms provided in both the first and second groups - Use your medical knowledge to understand and compare each Medical Service Name details - Provide a judgment score for the degree of similarity, along with a reason for the similarity score"""

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