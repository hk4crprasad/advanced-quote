from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
import random

# Try different import locations for StrOutputParser based on LangChain version
try:
    from langchain_core.output_parsers import StrOutputParser
except ImportError:
    try:
        from langchain.output_parsers import StrOutputParser
    except ImportError:
        # Fallback: Create a simple string output parser
        class StrOutputParser:
            def parse(self, text):
                return text if isinstance(text, str) else str(text)
            
            def __or__(self, other):
                return self
            
            def __call__(self, input_data):
                if hasattr(input_data, 'content'):
                    return input_data.content
                return str(input_data)

# Initialize the LLM with your LiteLLM configuration
llm = ChatOpenAI(
    openai_api_base="https://litellm.tecosys.ai/",
    openai_api_key="sk-LLPrAbLPEaAJIduZjOyRzw",
    model="cost-cut",
    temperature=0.8  # Higher temperature for more creative stories
)

# Create comprehensive prompt templates for different horror story types

# Template 1: Job Horror Stories
horror_job_story_template = """
आपका काम एक डरावनी कहानी लिखना है जो एक नई नौकरी के बारे में है।

कहानी की संरचना:
1. बधाई देकर शुरुआत करें
2. एक रहस्यमय/डरावनी जगह का वर्णन करें  
3. सरल काम का विवरण दें
4. समय के साथ विशिष्ट नियम/चेतावनी दें
5. अलौकिक तत्व शामिल करें
6. एक खुला अंत जो डर बनाए रखे

भाषा: हिंदी में लिखें
टोन: डरावना, रहस्यमय, तनावपूर्ण
लंबाई: 100-150 शब्द (1 मिनट से कम पढ़ने का समय)

नौकरी का प्रकार: {job_type}
स्थान: {location}
समय: {shift_time}

कृपया एक छोटी कहानी लिखें जो 1 मिनट में पढ़ी जा सके।
"""

# Template 2: General Horror Stories
horror_general_story_template = """
एक डरावनी कहानी लिखें जो निम्नलिखित विषय पर आधारित हो।

कहानी की संरचना:
1. एक सामान्य स्थिति से शुरुआत
2. धीरे-धीरे अजीब घटनाओं का वर्णन
3. तनाव बढ़ाते हुए रहस्यमय तत्व
4. अलौकिक या डरावने मोड़
5. दर्शकों को डराने वाला अंत

विषय: {theme}
स्थान: {setting}
मुख्य तत्व: {element}

भाषा: हिंदी में लिखें
टोन: डरावना, रोमांचक, तनावपूर्ण
लंबाई: 100-150 शब्द (1 मिनट से कम पढ़ने का समय)

कृपया एक छोटी और प्रभावशाली कहानी लिखें।
"""

# Create the prompt templates
job_prompt = ChatPromptTemplate.from_template(horror_job_story_template)
general_prompt = ChatPromptTemplate.from_template(horror_general_story_template)

# Create the processing chain (compatible with older LangChain versions)
def create_chain(prompt_template, llm):
    """Create a chain that works with different LangChain versions"""
    try:
        # Try modern chain syntax
        return prompt_template | llm | StrOutputParser()
    except:
        # Fallback for older versions
        def chain_invoke(inputs):
            formatted_prompt = prompt_template.format(**inputs)
            response = llm.invoke([HumanMessage(content=formatted_prompt)])
            return response.content if hasattr(response, 'content') else str(response)
        return type('Chain', (), {'invoke': chain_invoke})()

# Remove the old chain creation with undefined prompt
# chain = create_chain(prompt, llm)

# Predefined job types, locations, and shifts for variety
job_types = [
    "रेडियो स्टेशन का रात्रि प्रसारण",
    "पुराने अस्पताल की सफाई", 
    "कब्रिस्तान की सुरक्षा",
    "पुस्तकालय की रात्रि शिफ्ट",
    "फैक्ट्री की निगरानी",
    "स्कूल की रात्रि सफाई",
    "गैस स्टेशन का काउंटर",
    "होटल की रिसेप्शन",
    "मेट्रो स्टेशन की सुरक्षा"
]

locations = [
    "शहर के बाहर एक वीरान पहाड़ी पर",
    "घने जंगल के बीच छुपा हुआ",
    "नदी के किनारे एक पुराना",
    "खेतों के बीच में अकेला",
    "पुराने कारखाने के इलाके में",
    "रेगिस्तान के बीचों-बीच",
    "पहाड़ों की गुफा के पास",
    "समुद्र के किनारे एक टूटा हुआ"
]

shift_times = [
    "रात 10 से सुबह 6 बजे तक",
    "रात 11 से सुबह 7 बजे तक", 
    "रात 9 से सुबह 5 बजे तक",
    "रात 12 से सुबह 8 बजे तक"
]

# General horror story elements
horror_themes = [
    "भूतिया फोन कॉल",
    "गुमशुदा बच्चे",
    "पुराना घर",
    "जादुई आईना",
    "श्रापित वस्तु",
    "अजनबी का पीछा",
    "रात का सफर",
    "टूटा हुआ लिफ्ट",
    "अंधेरी सुरंग"
]

horror_settings = [
    "एक पुराने मकान में",
    "घने जंगल के बीच",
    "टूटी हुई सड़क पर",
    "खाली अस्पताल में",
    "रेगिस्तान के बीच",
    "समुद्र के किनारे",
    "पहाड़ की चोटी पर",
    "भूमिगत तहखाने में",
    "परित्यक्त स्कूल में"
]

horror_elements = [
    "अदृश्य आवाजें",
    "खुद से हिलने वाली चीजें",
    "गायब होते लोग",
    "समय का रुक जाना",
    "छायाओं का नृत्य",
    "खून के निशान",
    "टूटे हुए शीशे",
    "ठंडी हवा का झोंका",
    "अजीब महक"
]

# Story type selection
STORY_TYPES = ["job", "general"]

def generate_job_horror_story(custom_job=None, custom_location=None, custom_shift=None):
    """
    Generate a job-based horror story with random or custom parameters
    """
    job = custom_job or random.choice(job_types)
    location = custom_location or random.choice(locations)
    shift = custom_shift or random.choice(shift_times)
    
    job_chain = create_chain(job_prompt, llm)
    
    try:
        story = job_chain.invoke({
            "job_type": job,
            "location": location, 
            "shift_time": shift
        })
        return story
    except Exception as e:
        return f"जॉब कहानी बनाने में त्रुटि: {str(e)}"

def generate_general_horror_story(custom_theme=None, custom_setting=None, custom_element=None):
    """
    Generate a general horror story with random or custom parameters
    """
    theme = custom_theme or random.choice(horror_themes)
    setting = custom_setting or random.choice(horror_settings)
    element = custom_element or random.choice(horror_elements)
    
    general_chain = create_chain(general_prompt, llm)
    
    try:
        story = general_chain.invoke({
            "theme": theme,
            "setting": setting,
            "element": element
        })
        return story
    except Exception as e:
        return f"सामान्य कहानी बनाने में त्रुटि: {str(e)}"

def generate_random_horror_story():
    """
    Randomly select between job horror story or general horror story
    """
    story_type = random.choice(STORY_TYPES)
    
    if story_type == "job":
        print("🏢 Generating Job Horror Story...")
        return generate_job_horror_story()
    else:
        print("👻 Generating General Horror Story...")
        return generate_general_horror_story()

def generate_horror_story(custom_job=None, custom_location=None, custom_shift=None):
    """
    Backward compatibility function - generates random story type
    """
    return generate_random_horror_story()

def generate_multiple_stories(count=3):
    """
    Generate multiple horror stories with random types
    """
    stories = []
    for i in range(count):
        print(f"\n{'='*50}")
        print(f"कहानी #{i+1}")
        print('='*50)
        
        story = generate_random_horror_story()
        stories.append(story)
        print(story)
        
    return stories

# Enhanced story generator with more specific prompts
class HorrorStoryGenerator:
    def __init__(self, llm):
        self.llm = llm
        self.rules_template = """
        इस डरावनी कहानी के लिए 3-4 संक्षिप्त समय-आधारित नियम बनाएं:
        
        नौकरी: {job_type}
        स्थान: {location}
        
        नियम इस प्रकार के हों:
        - विशिष्ट समय के साथ
        - अलौकिक घटनाओं के बारे में
        - बहुत संक्षिप्त और स्पष्ट
        - 1 मिनट की कहानी के लिए उपयुक्त
        
        उदाहरण:
        **11:00 बजे**, लाइट बंद कर देना।
        """
    
    def generate_rules(self, job_type, location):
        """Generate specific rules for the story"""
        rules_prompt = ChatPromptTemplate.from_template(self.rules_template)
        rules_chain = create_chain(rules_prompt, self.llm)
        
        return rules_chain.invoke({
            "job_type": job_type,
            "location": location
        })
    
    def generate_complete_story(self, job_type=None, location=None):
        """Generate a complete story with custom rules"""
        job = job_type or random.choice(job_types)
        loc = location or random.choice(locations)
        
        rules = self.generate_rules(job, loc)
        
        complete_template = """
        बधाई हो। आपको '{job_type}' की नौकरी मिली है।
        
        यह {location} स्थित है। 
        
        काम सरल है... लेकिन कुछ नियम हैं:
        
        {rules}
        
        कृपया इसे एक छोटी डरावनी कहानी के रूप में तैयार करें।
        महत्वपूर्ण: 100-150 शब्दों में (1 मिनट से कम)।
        """
        
        final_prompt = ChatPromptTemplate.from_template(complete_template)
        final_chain = create_chain(final_prompt, self.llm)
        
        return final_chain.invoke({
            "job_type": job,
            "location": loc,
            "rules": rules
        })

# Initialize the enhanced generator
enhanced_generator = HorrorStoryGenerator(llm)

# Additional utility functions
def get_story_type_examples():
    """Show examples of what each story type generates"""
    print("📖 Story Type Examples:")
    print("\n1. Job Horror Story:")
    print("   - बधाई हो! आपको रेडियो स्टेशन की नौकरी मिली है...")
    print("   - Focus: Workplace horror with specific rules and schedules")
    
    print("\n2. General Horror Story:")
    print("   - भूतिया फोन कॉल के बारे में कहानी...")
    print("   - Focus: Traditional horror themes with supernatural elements")

def generate_specific_type_story(story_type="random"):
    """
    Generate a specific type of horror story
    Args:
        story_type: "job", "general", or "random"
    """
    if story_type == "job":
        return generate_job_horror_story()
    elif story_type == "general":
        return generate_general_horror_story()
    else:
        return generate_random_horror_story()
