
import os
import json
import re
from openai import OpenAI
import streamlit as st # For st.error, st.warning
from typing import List, Dict, Any, Tuple, Optional
from utils import remove_problematic_chars # Assuming utils.py is in the same directory
from document_processing import extract_sections_from_rfp # Assuming document_processing.py is in the same directory
from knowledge_base import ProposalKnowledgeBase # For type hinting and potential direct use if necessary, or pass kb instance
from sklearn.feature_extraction.text import TfidfVectorizer # For identify_gaps_and_risks
from sklearn.metrics.pairwise import cosine_similarity # For identify_gaps_and_risks
# expand_query might be called from here, ensure it's accessible (e.g., from knowledge_base.py or utils.py)
from knowledge_base import expand_query



class SpecialistRAGDrafter:
    def __init__(self, openai_key=None):
        self.client = OpenAI(api_key=openai_key or os.environ.get("OPENAI_API_KEY"))

    def generate_draft(self, section_name, rfp_section_content, relevant_kb_content, client_name):
        # Ensure all input text is cleaned before sending to LLM
        cleaned_section_name = remove_problematic_chars(section_name)
        cleaned_rfp_section_content = remove_problematic_chars(rfp_section_content) if rfp_section_content else ""
        cleaned_client_name = remove_problematic_chars(client_name) if client_name else ""

        kb_blob = "\n\n".join([
            f"--- {('Very Relevant' if item['score']>0.7 else 'Relevant')} PAST PROPOSAL ---\n"
            f"From: {remove_problematic_chars(item['document']['filename'])} | Section: {remove_problematic_chars(item['document']['section_name'])}\n"
            f"{remove_problematic_chars(item['document']['content'])}"
            for item in relevant_kb_content
        ])

        summary_resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You’re an expert at summarizing past proposals."},
                {"role":"user","content":
                    f"Summarize the following past-proposal content into 5–7 bullets, focusing on actionable points:\n\n{kb_blob}"
                }
            ],
            temperature=0.0
        )
        # Clean the summarized KB content from the LLM
        summarized_kb = remove_problematic_chars(summary_resp.choices[0].message.content)

        prompt = f"""
        # DRAFT GENERATION FOR {cleaned_section_name}

        ## SECTION CONTENT TO ADDRESS
        {cleaned_rfp_section_content}

        ## SUMMARY OF PAST PROPOSALS
        {summarized_kb}
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            # Clean the generated draft text
            return remove_problematic_chars(response.choices[0].message.content)
        except Exception as e:
            return f"Error generating draft for {cleaned_section_name}: {str(e)}"

    def generate_rfp_template(self, company_objectives, template_type):
        # Ensure input text is cleaned before sending to LLM
        cleaned_company_objectives = remove_problematic_chars(company_objectives)
        cleaned_template_type = remove_problematic_chars(template_type)

        prompt = f"""
        # RFP TEMPLATE GENERATION

        Create a comprehensive RFP template based on the following company objectives and template type:

        COMPANY OBJECTIVES:
        {cleaned_company_objectives}

        TEMPLATE TYPE:
        {cleaned_template_type}

        The template should include:
        1. All standard sections for the selected template type
        2. Custom sections based on the company objectives
        3. Clear structure with appropriate headings and subheadings
        4. Placeholder content where applicable
        5. Evaluation criteria section tailored to the objectives
        6. Submission guidelines

        Format as a professional RFP document.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            # Clean the generated template text
            return remove_problematic_chars(response.choices[0].message.content)
        except Exception as e:
            return f"Error generating RFP template: {str(e)}"
        
        
# Enhanced SOW Extraction Module for generation_engine.py

class EnhancedSOWExtractor:
    """Enhanced Scope of Work extraction and structuring capabilities"""
    
    def __init__(self, openai_client):
        self.client = openai_client
    
    def extract_complete_requirements(self, rfp_text):
        """Extract all detailed requirements from RFP to ensure comprehensive SOW coverage"""
        
        cleaned_rfp_text = remove_problematic_chars(rfp_text)
        
        prompt = f"""
        # COMPREHENSIVE REQUIREMENTS EXTRACTION
        
        Analyze the following RFP text and extract ALL detailed requirements to ensure complete SOW coverage.
        
        ## RFP TEXT:
        {cleaned_rfp_text}
        
        ## EXTRACTION INSTRUCTIONS:
        Extract and categorize ALL requirements into the following structured format:
        
        ### 1. FUNCTIONAL REQUIREMENTS
        - Core business functions that must be delivered
        - User capabilities and features required
        - System functionalities and operations
        
        ### 2. TECHNICAL REQUIREMENTS
        - Technology specifications and standards
        - Integration requirements
        - Performance and scalability needs
        - Security and compliance requirements
        - Infrastructure and platform requirements
        
        ### 3. OPERATIONAL REQUIREMENTS
        - Service level agreements (SLAs)
        - Support and maintenance needs
        - Training and documentation requirements
        - Operational procedures and processes
        
        ### 4. BUSINESS REQUIREMENTS
        - Strategic objectives and goals
        - Business process requirements
        - Stakeholder needs and expectations
        - Success criteria and metrics
        
        ### 5. DELIVERY REQUIREMENTS
        - Timeline and milestone requirements
        - Resource and staffing requirements
        - Quality assurance and testing needs
        - Implementation and deployment requirements
        
        ### 6. COMPLIANCE & REGULATORY REQUIREMENTS
        - Legal and regulatory compliance
        - Industry standards and certifications
        - Data protection and privacy requirements
        - Audit and reporting requirements
        
        For each requirement category, provide:
        - Specific requirement statements (quoted from RFP where possible)
        - Priority level (Critical/High/Medium/Low)
        - Dependencies or constraints
        - Acceptance criteria or success measures
        
        Format your response with clear headings and bullet points for each category.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            return remove_problematic_chars(response.choices[0].message.content)
        except Exception as e:
            return f"Error extracting comprehensive requirements: {str(e)}"
    
    def structure_scope_of_work(self, requirements_text, rfp_analysis):
        """Create a structured and detailed SOW with tasks, sub-tasks, and deliverables"""
        
        cleaned_requirements = remove_problematic_chars(requirements_text)
        cleaned_rfp_analysis = remove_problematic_chars(rfp_analysis)
        
        prompt = f"""
        # SCOPE OF WORK STRUCTURING
        
        Based on the extracted requirements and RFP analysis, create a comprehensive structured SOW.
        
        ## REQUIREMENTS ANALYSIS:
        {cleaned_requirements}
        
        ## RFP CONTEXT:
        {cleaned_rfp_analysis}
        
        ## SOW STRUCTURE INSTRUCTIONS:
        Create a detailed SOW with the following hierarchical structure:
        
        ### PHASE/WORKSTREAM LEVEL
        Organize work into logical phases or workstreams
        
        ### TASK LEVEL
        For each phase, define major tasks that group related activities
        
        ### SUB-TASK LEVEL
        Break down each task into specific, actionable sub-tasks
        
        ### DELIVERABLE LEVEL
        Identify concrete deliverables for each task/sub-task
        
        ### SUB-DELIVERABLE LEVEL
        Detail components of major deliverables
        
        ## OUTPUT FORMAT:
        
        ### PHASE 1: [Phase Name]
        **Objective:** [Clear statement of phase objective]
        **Duration:** [Estimated timeline]
        **Key Stakeholders:** [Primary stakeholders involved]
        
        #### TASK 1.1: [Task Name]
        **Description:** [Detailed task description]
        **Dependencies:** [Prerequisites or dependencies]
        **Success Criteria:** [How success is measured]
        
        ##### SUB-TASK 1.1.1: [Sub-task Name]
        - **Activities:** [Specific activities to be performed]
        - **Resources Required:** [Skills, tools, or resources needed]
        - **Timeline:** [Estimated duration]
        
        ##### DELIVERABLE 1.1.A: [Deliverable Name]
        - **Type:** [Document/System/Process/etc.]
        - **Format:** [Specific format requirements]
        - **Acceptance Criteria:** [Criteria for acceptance]
        
        ###### SUB-DELIVERABLE 1.1.A.1: [Component Name]
        - **Description:** [Detailed description]
        - **Specifications:** [Technical or quality specifications]
        
        Continue this structure for all phases, tasks, sub-tasks, and deliverables.
        
        Ensure the SOW is:
        - Comprehensive and covers all extracted requirements
        - Logically organized and easy to follow
        - Specific and actionable
        - Measurable and verifiable
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return remove_problematic_chars(response.choices[0].message.content)
        except Exception as e:
            return f"Error structuring SOW: {str(e)}"
    
    def extract_bill_of_quantities(self, structured_sow, rfp_text):
        """Extract comprehensive bill of quantities from the structured SOW"""
        
        cleaned_sow = remove_problematic_chars(structured_sow)
        cleaned_rfp_text = remove_problematic_chars(rfp_text)
        
        prompt = f"""
        # BILL OF QUANTITIES EXTRACTION
        
        Based on the structured SOW and original RFP, create a comprehensive Bill of Quantities (BOQ).
        
        ## STRUCTURED SOW:
        {cleaned_sow}
        
        ## ORIGINAL RFP CONTEXT:
        {cleaned_rfp_text}
        
        ## BOQ EXTRACTION INSTRUCTIONS:
        Extract and quantify all items from the SOW to create a detailed BOQ that includes:
        
        ### 1. TASK QUANTITIES
        - Number of tasks and sub-tasks
        - Estimated effort hours per task
        - Resource requirements per task
        - Complexity ratings
        
        ### 2. DELIVERABLE QUANTITIES
        - Count of each type of deliverable
        - Size/scope metrics (pages, features, components)
        - Quality requirements and standards
        - Review and approval cycles
        
        ### 3. RESOURCE QUANTITIES
        - Human resources by role/skill level
        - Time allocation per resource type
        - Equipment and tool requirements
        - Third-party services or licenses
        
        ### 4. TIMELINE QUANTITIES
        - Phase durations
        - Critical path activities
        - Buffer times and contingencies
        - Milestone dates and dependencies
        
        ### 5. QUALITY ASSURANCE QUANTITIES
        - Testing cycles and iterations
        - Review sessions and checkpoints
        - Documentation and training hours
        - Compliance verification activities
        
        ## OUTPUT FORMAT:
        
        ### EXECUTIVE SUMMARY
        - Total project duration: [X weeks/months]
        - Total effort estimate: [X person-hours/days]
        - Number of major deliverables: [X]
        - Number of phases/workstreams: [X]
        
        ### DETAILED BOQ TABLE
        | Category | Item | Quantity | Unit | Description | Dependencies |
        |----------|------|----------|------|-------------|--------------|
        | Tasks | [Task Name] | [Hours] | Person-hours | [Description] | [Dependencies] |
        | Deliverables | [Deliverable] | [Count] | Units | [Specifications] | [Prerequisites] |
        | Resources | [Resource Type] | [Amount] | [Unit] | [Role/Skill] | [Availability] |
        
        ### ASSUMPTIONS AND CONSTRAINTS
        - List key assumptions made in quantity estimation
        - Identify potential constraints or risks
        - Note any items requiring client clarification
        
        Ensure all quantities are:
        - Realistic and well-justified
        - Aligned with the structured SOW
        - Comprehensive and complete
        - Clearly defined and measurable
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            return remove_problematic_chars(response.choices[0].message.content)
        except Exception as e:
            return f"Error extracting bill of quantities: {str(e)}"
    
    def generate_executive_summary_with_sow(self, sow_structure, bill_of_quantities, client_strategic_goals, rfp_analysis):
        """Generate an executive summary that ties SOW with client's strategic goals"""
        
        cleaned_sow = remove_problematic_chars(sow_structure)
        cleaned_boq = remove_problematic_chars(bill_of_quantities)
        cleaned_goals = remove_problematic_chars(client_strategic_goals)
        cleaned_rfp = remove_problematic_chars(rfp_analysis)
        
        prompt = f"""
        # STRATEGIC EXECUTIVE SUMMARY GENERATION
        
        Create a comprehensive executive summary that connects the detailed SOW with the client's strategic goals and priorities.
        
        ## INPUTS:
        
        ### SOW STRUCTURE:
        {cleaned_sow}
        
        ### BILL OF QUANTITIES:
        {cleaned_boq}
        
        ### CLIENT STRATEGIC GOALS:
        {cleaned_goals}
        
        ### RFP ANALYSIS:
        {cleaned_rfp}
        
        ## EXECUTIVE SUMMARY REQUIREMENTS:
        
        ### 1. STRATEGIC ALIGNMENT
        - How the SOW directly supports client's strategic objectives
        - Connection between proposed deliverables and business goals
        - Value proposition and expected business outcomes
        
        ### 2. SOW OVERVIEW
        - High-level summary of the structured approach
        - Key phases and major milestones
        - Critical success factors and dependencies
        
        ### 3. DELIVERY FRAMEWORK
        - Methodology and approach overview
        - Quality assurance and risk management
        - Stakeholder engagement and communication plan
        
        ### 4. RESOURCE AND TIMELINE SUMMARY
        - Total effort and duration estimates
        - Key resource requirements and expertise
        - Critical milestones and delivery schedule
        
        ### 5. VALUE REALIZATION
        - Expected benefits and outcomes
        - Success metrics and KPIs
        - Long-term value and sustainability
        
        ### 6. NEXT STEPS
        - Immediate actions and decisions required
        - Project initiation and kickoff process
        - Key dependencies and prerequisites
        
        ## OUTPUT FORMAT:
        Structure the executive summary as a compelling narrative that:
        - Opens with client's strategic context and challenges
        - Presents our understanding of their priorities
        - Outlines our structured SOW approach
        - Demonstrates clear value alignment
        - Closes with confident next steps
        
        Keep the summary:
        - Concise but comprehensive (800-1200 words)
        - Executive-focused and strategic
        - Clear and jargon-free
        - Action-oriented and compelling
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            return remove_problematic_chars(response.choices[0].message.content)
        except Exception as e:
            return f"Error generating strategic executive summary: {str(e)}"

    
    
    

class EnhancedProposalGenerator:
    def __init__(self, knowledge_base, openai_key=None):
        self.kb = knowledge_base
        self.client = OpenAI(api_key=openai_key or os.environ.get("OPENAI_API_KEY"))
        self.rfp_text = None  # Store RFP text for regeneration
        self.drafter = SpecialistRAGDrafter(openai_key)  # Specialist drafter

    def analyze_rfp(self, rfp_text):
        """Comprehensive RFP analysis with additional metadata extraction"""
        # Clean RFP text before storing and sending to LLM
        cleaned_rfp_text = remove_problematic_chars(rfp_text)
        self.rfp_text = cleaned_rfp_text

        prompt = f"""
        You are an expert proposal analyst. Your task is to analyze the following Request for Proposal (RFP) text and extract key information.
        I need a comprehensive, structured analysis of the following Request for Proposal (RFP). Please organize your analysis into the following specific categories with clear headings:

        1. KEY REQUIREMENTS: Extract specific functional and technical requirements that must be addressed, using exact language from the RFP where possible.

        2. DELIVERABLES: List all concrete deliverables explicitly requested in the RFP.

        3. REQUIRED SECTIONS: Identify EXACTLY what sections must be included in the proposal response. Include both main sections and any specified subsections. Use the exact section names from the RFP.

        4. TIMELINE: Extract all dates, deadlines, and milestones mentioned in the RFP.

        5. BUDGET CONSTRAINTS: Note any explicit budget limitations, pricing structures, or financial parameters mentioned.

        6. EVALUATION CRITERIA: Detail how the proposal will be scored or evaluated, including any weighted criteria.

        7. CLIENT PAIN POINTS: Identify specific problems or challenges the client is trying to solve, both explicit and implied.

        8. UNIQUE CONSIDERATIONS: Flag any special requirements, unusual constraints, or differentiating factors that stand out.

        9. RFP METADATA: Extract the following specific metadata from the RFP:
        - CLIENT NAME: The organization issuing this RFP
        - PROJECT TITLE: The official title of the project
        - PROJECT OBJECTIVES: Main goals of the project
        - PROJECT DURATION: Expected timeline or duration
        - TARGET AUDIENCE: Who will benefit from or use the deliverables
        - PROJECT LOCATION: Where the project will be implemented
        - NUMBER OF PARTICIPANTS: How many people will be involved
        - DELIVERY LANGUAGE: Required language for deliverables
        - DEADLINE OF BID SUBMISSION: When the proposal must be submitted (if in Hijri calendar, please also convert to Gregorian calendar)

        Format your response as a structured analysis with clear headings for each category. Use bullet points for clarity. Extract specific, actionable information rather than general observations.

        RFP TEXT:
        {cleaned_rfp_text}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )

            # Clean the generated analysis text
            analysis_result = remove_problematic_chars(response.choices[0].message.content)
            
            # Extract metadata for session state
            metadata = {}
            metadata_section = re.search(r"RFP METADATA(.*?)(?:\n\n|$)", analysis_result, re.DOTALL)
            if metadata_section:
                metadata_text = metadata_section.group(1).strip()
                # Extract each metadata field
                client_name = re.search(r"CLIENT NAME:?\s*(.*?)(?:\n|$)", metadata_text)
                metadata['client_name'] = client_name.group(1).strip() if client_name else "Not specified"
                
                project_title = re.search(r"PROJECT TITLE:?\s*(.*?)(?:\n|$)", metadata_text)
                metadata['project_title'] = project_title.group(1).strip() if project_title else "Not specified"
                
                project_objectives = re.search(r"PROJECT OBJECTIVES:?\s*(.*?)(?:\n|$)", metadata_text)
                metadata['project_objectives'] = project_objectives.group(1).strip() if project_objectives else "Not specified"
                
                project_duration = re.search(r"PROJECT DURATION:?\s*(.*?)(?:\n|$)", metadata_text)
                metadata['project_duration'] = project_duration.group(1).strip() if project_duration else "Not specified"
                
                target_audience = re.search(r"TARGET AUDIENCE:?\s*(.*?)(?:\n|$)", metadata_text)
                metadata['target_audience'] = target_audience.group(1).strip() if target_audience else "Not specified"
                
                project_location = re.search(r"PROJECT LOCATION:?\s*(.*?)(?:\n|$)", metadata_text)
                metadata['project_location'] = project_location.group(1).strip() if project_location else "Not specified"
                
                participants = re.search(r"NUMBER OF PARTICIPANTS:?\s*(.*?)(?:\n|$)", metadata_text)
                metadata['participants'] = participants.group(1).strip() if participants else "Not specified"
                
                delivery_language = re.search(r"DELIVERY LANGUAGE:?\s*(.*?)(?:\n|$)", metadata_text)
                metadata['delivery_language'] = delivery_language.group(1).strip() if delivery_language else "Not specified"
                
                submission_deadline = re.search(r"DEADLINE OF BID SUBMISSION:?\s*(.*?)(?:\n|$)", metadata_text)
                metadata['submission_deadline'] = submission_deadline.group(1).strip() if submission_deadline else "Not specified"
                
            # Store metadata in session state for use across tabs
            st.session_state.rfp_metadata = metadata
            
            return analysis_result
        except Exception as e:
            print(f"Error analyzing RFP: {str(e)}")
            return f"Error analyzing RFP: {str(e)}"

    def extract_mandatory_criteria(self, rfp_analysis):
        """Extract mandatory criteria from RFP analysis"""
        # Ensure input analysis text is cleaned
        cleaned_rfp_analysis = remove_problematic_chars(rfp_analysis)
        try:
            requirements_start = cleaned_rfp_analysis.find("KEY REQUIREMENTS") + len("KEY REQUIREMENTS")
            requirements_end = cleaned_rfp_analysis.find("DELIVERABLES", requirements_start)
            requirements_text = cleaned_rfp_analysis[requirements_start:requirements_end].strip()

            mandatory_criteria = []
            for line in requirements_text.split('\n'):
                if line.strip() and ("must" in line.lower() or "required" in line.lower()):
                    # Clean each extracted criterion
                    mandatory_criteria.append(remove_problematic_chars(line.strip()))

            return mandatory_criteria
        except:
            return []

    def extract_weighted_criteria(self, rfp_analysis):
        """Extract weighted evaluation criteria from RFP analysis"""
        # Ensure input analysis text is cleaned
        cleaned_rfp_analysis = remove_problematic_chars(rfp_analysis)
        try:
            criteria_start = cleaned_rfp_analysis.find("EVALUATION CRITERIA") + len("EVALUATION CRITERIA")
            criteria_end = cleaned_rfp_analysis.find("CLIENT PAIN POINTS", criteria_start)
            criteria_text = cleaned_rfp_analysis[criteria_start:criteria_end].strip()

            weighted_criteria = []
            for line in criteria_text.split('\n'):
                if line.strip():
                    match = re.match(r'^(.*?)(\s+\((\d+)%\))?', line.strip())
                    if match:
                        criterion = remove_problematic_chars(match.group(1).strip()) # Clean criterion text
                        weight = int(match.group(3)) if match.group(3) else 100 # Default to 100 if weight not specified
                        weighted_criteria.append((criterion, weight))
            # Default weights if none are found explicitly in RFP analysis
            if not weighted_criteria:
                 # These defaults are used if the RFP analysis doesn't explicitly list weighted criteria
                 weighted_criteria = [("Requirement Match", 40), ("Compliance", 25), ("Quality", 20), ("Alignment", 15)] # Example defaults
            return weighted_criteria
        except:
            # Return some default criteria if parsing fails
            return [("Requirement Match", 40), ("Compliance", 25), ("Quality", 20), ("Alignment", 15)]


    def extract_deadlines(self, rfp_analysis):
        """Extract deadlines from RFP analysis"""
        # Ensure input analysis text is cleaned
        cleaned_rfp_analysis = remove_problematic_chars(rfp_analysis)
        try:
            timeline_start = cleaned_rfp_analysis.find("TIMELINE") + len("TIMELINE")
            timeline_end = cleaned_rfp_analysis.find("\n\n", timeline_start)
            timeline_text = cleaned_rfp_analysis[timeline_start:timeline_end].strip()

            deadlines = []
            for line in timeline_text.split('\n'):
                if line.strip() and any(term in line.lower() for term in ["deadline", "date", "due"]):
                    # Clean each extracted deadline
                    deadlines.append(remove_problematic_chars(line.strip()))

            return deadlines
        except:
            return []

    def extract_deliverables(self, rfp_analysis):
        """Extract deliverables from RFP analysis"""
        # Ensure input analysis text is cleaned
        cleaned_rfp_analysis = remove_problematic_chars(rfp_analysis)
        try:
            deliverables_start = cleaned_rfp_analysis.find("DELIVERABLES") + len("DELIVERABLES")
            deliverables_end = cleaned_rfp_analysis.find("\n\n", deliverables_start)
            deliverables_text = cleaned_rfp_analysis[deliverables_start:deliverables_end].strip()

            deliverables = []
            for line in deliverables_text.split('\n'):
                if line.strip():
                    # Clean each extracted deliverable
                    deliverables.append(remove_problematic_chars(line.strip()))

            return deliverables
        except:
            return []

    def assess_compliance(self, rfp_analysis, internal_capabilities):
        """Assess compliance with internal capabilities"""
        # Ensure input analysis text is cleaned
        cleaned_rfp_analysis = remove_problematic_chars(rfp_analysis)
        try:
            requirements_pattern = r"KEY REQUIREMENTS(.*?)DELIVERABLES"
            requirements_text = re.search(requirements_pattern, cleaned_rfp_analysis, re.DOTALL)
            requirements_text = requirements_text.group(1).strip() if requirements_text else ""

            # Ensure internal capabilities strings are cleaned
            cleaned_internal_capabilities = {
                key: [remove_problematic_chars(item) for item in value]
                for key, value in internal_capabilities.items()
            }


            prompt = f"""
            Assess compliance between RFP requirements and internal capabilities:

            RFP REQUIREMENTS:
            {requirements_text}

            INTERNAL CAPABILITIES:
            Technical: {', '.join(cleaned_internal_capabilities.get('technical', []))}
            Functional: {', '.join(cleaned_internal_capabilities.get('functional', []))}

            For each RFP requirement, determine if we can:
            - Fully comply
            - Partially comply

            Flag any requirements where we have significant gaps. Provide specific explanations for each compliance status.

            Format your response as a structured markdown table with columns:
            | Requirement | Compliance Status | Explanation |
            """

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            # Clean the generated compliance assessment text
            return remove_problematic_chars(response.choices[0].message.content)
        except Exception as e:
            print(f"Error assessing compliance: {str(e)}")
            return "Error assessing compliance."

    def extract_required_sections(self, rfp_analysis):
        """Extract required sections from RFP analysis"""
        # Ensure input analysis text is cleaned
        cleaned_rfp_analysis = remove_problematic_chars(rfp_analysis)
        try:
            sections_start = cleaned_rfp_analysis.find("REQUIRED SECTIONS") + len("REQUIRED SECTIONS")
            sections_end = cleaned_rfp_analysis.find("\n\n", sections_start)
            sections_text = cleaned_rfp_analysis[sections_start:sections_end].strip()
            # Clean each extracted section name
            sections = [remove_problematic_chars(s.strip()) for s in sections_text.split("\n") if s.strip()]
            return sections
        except:
            return []

    def generate_section(self, section_name, rfp_analysis, rfp_section_content,
                         client_background, differentiators,
                         evaluation_criteria, relevant_kb_content, client_name):
        """Generate a proposal section with checks for KB availability for pricing."""

        # Inputs are assumed to be cleaned by the calling function (generate_full_proposal)
        # For safety, we can re-apply cleaning here if called directly elsewhere.
        cleaned_section_name = remove_problematic_chars(section_name)
        cleaned_rfp_analysis = remove_problematic_chars(rfp_analysis)
        cleaned_rfp_section_content = remove_problematic_chars(rfp_section_content) if rfp_section_content else ""
        cleaned_client_background = remove_problematic_chars(client_background) if client_background else ""
        cleaned_differentiators = remove_problematic_chars(differentiators) if differentiators else ""
        cleaned_evaluation_criteria = remove_problematic_chars(evaluation_criteria) if evaluation_criteria else ""
        cleaned_client_name = remove_problematic_chars(client_name) if client_name else ""

        # relevant_kb_content is a list of dicts; ensure content within is cleaned
        cleaned_relevant_kb_content = []
        for item in relevant_kb_content:
            if isinstance(item, dict) and 'document' in item and isinstance(item['document'], dict):
                 item['document']['filename'] = remove_problematic_chars(item['document'].get('filename', ''))
                 item['document']['section_name'] = remove_problematic_chars(item['document'].get('section_name', ''))
                 item['document']['content'] = remove_problematic_chars(item['document'].get('content', ''))
                 cleaned_relevant_kb_content.append(item)
            # else: skip malformed items


        is_pricing = any(term in cleaned_section_name.lower() for term in ["commercial", "pricing", "cost", "financial", "budget", "price"])

        pricing_block = ""
        if is_pricing:
            # --- ADDED CHECK for KB before accessing pricing ---
            if not self.kb or not hasattr(self.kb, 'extract_pricing_from_kb'):
                st.warning(f"Knowledge Base unavailable for pricing insights in section '{cleaned_section_name}'.")
                pricing_block = "\n\n## PRICING INSIGHT\nKnowledge Base unavailable."
                prices = [] # Define prices as empty list
            else:
                try:
                    prices = self.kb.extract_pricing_from_kb() # Method returns list of ints
                    if prices:
                        avg = sum(prices) / len(prices)
                        pricing_block = (
                            f"\n\n## PRICING INSIGHT\n"
                            f"Based on {len(prices)} past proposals, prices ranged from ₹{min(prices):,} "
                            f"to ₹{max(prices):,}, with an average of ₹{avg:,.0f}."
                        )
                    else:
                        pricing_block = "\n\n## PRICING INSIGHT\nNo past pricing data found in KB."
                except Exception as e:
                    st.error(f"Error extracting pricing from KB: {e}")
                    pricing_block = "\n\n## PRICING INSIGHT\nError extracting pricing data from KB."
                    prices = [] # Define prices as empty list on error
            # --- END CHECK ---
        else:
             prices = [] # Ensure prices is defined if not a pricing section

        # Prepare KB items string from the cleaned list
        kb_items = "\n\n".join([
             f"--- {('Very Relevant' if item.get('score', 0)>0.8 else 'Relevant')} PAST PROPOSAL ---\n"
             f"From: {item['document']['filename']} | Section: {item['document']['section_name']}\n"
             f"{item['document']['content']}" # Content is already cleaned
             for item in cleaned_relevant_kb_content if item.get('score', 0) >= 0.5
        ])[:2000] # Limit length

        # Ensure all parts of the prompt are cleaned strings
        prompt = f"""
        # STRATEGIC PROPOSAL SECTION GENERATION

        Section to Create: \"{cleaned_section_name}\"

        RFP CONTEXT:
        {cleaned_rfp_analysis}

        CLIENT BACKGROUND:
        {cleaned_client_background}

        EVALUATION CRITERIA:
        {cleaned_evaluation_criteria}

        DIFFERENTIATORS:
        {cleaned_differentiators}

        REFERENCE MATERIAL:
        {remove_problematic_chars(kb_items)}

        GENERATION INSTRUCTIONS:
        1. Address RFP requirements for '{cleaned_section_name}'.
        2. Use client-specific language and examples where possible, referring to '{cleaned_client_name}'.
        3. Incorporate relevant details from REFERENCE MATERIAL without direct copying.
        4. Highlight how our differentiators ({cleaned_differentiators}) meet the client's needs in this section.
        5. Ensure professional tone and clear structure.
        6. Only include explicit pricing details if this is a commercial/pricing section.
        {remove_problematic_chars(pricing_block)}
        """
        try:
            res = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"system","content":"You are an expert proposal writer, tailoring content specifically for the client and RFP section."},
                          {"role":"user","content":prompt}],
                temperature=0.2
            )
            # Clean the generated section content before returning
            return remove_problematic_chars(res.choices[0].message.content)
        except Exception as e:
            st.error(f"Error generating section '{cleaned_section_name}' via LLM: {e}")
            return f"Error generating section {cleaned_section_name}: {str(e)}" # Return cleaned error message

    def validate_proposal_client_specificity(self, proposal_sections, client_name):
        """Validates that the proposal is sufficiently client-specific"""
        issues = []
        # Ensure client name is cleaned for comparison
        cleaned_client_name = remove_problematic_chars(client_name) if client_name else ""

        for section_name, content in proposal_sections.items():
            # Ensure section name and content are cleaned for validation
            cleaned_section_name = remove_problematic_chars(section_name)
            cleaned_content = remove_problematic_chars(content)

            client_name_count = cleaned_content.lower().count(cleaned_client_name.lower())
            content_length = len(cleaned_content)

            expected_mentions = max(3, content_length // 500)

            if cleaned_client_name and client_name_count < expected_mentions:
                issues.append(f"Section '{cleaned_section_name}' has insufficient client references ({client_name_count} found, {expected_mentions} expected)")

            generic_phrases = [
                "our clients", "many organizations", "typical companies",
                "best practices", "industry standards", "our approach",
                "our methodology", "our process", "our solution"
            ]

            for phrase in generic_phrases:
                if phrase in cleaned_content.lower():
                    issues.append(f"Section '{cleaned_section_name}' contains generic phrase: '{phrase}'")

        return issues

    def refine_section(self, section_name, current_content, feedback, client_name):
        """Refine a section based on user feedback"""
        # Ensure all input text is cleaned before sending to LLM
        cleaned_section_name = remove_problematic_chars(section_name)
        cleaned_current_content = remove_problematic_chars(current_content)
        cleaned_feedback = remove_problematic_chars(feedback)
        cleaned_client_name = remove_problematic_chars(client_name) if client_name else ""

        # Perform replacements on cleaned content
        cleaned_current_content = cleaned_current_content.replace("CLIENT_NAME", cleaned_client_name)
        cleaned_current_content = cleaned_current_content.replace("COMPANY_NAME", "Your Company Name") # Assuming company name is safe ASCII

        prompt = f"""
        # SECTION REFINEMENT

        ## CURRENT SECTION CONTENT
        {cleaned_current_content}

        ## USER FEEDBACK
        {cleaned_feedback}

        ## REFINEMENT INSTRUCTIONS
        Revise the section to address the feedback provided. Maintain the professional tone and structure while incorporating the suggested improvements. If the feedback suggests adding specific information, ensure it's included in a relevant part of the section. If the feedback suggests restructuring, improve the organization while preserving all essential content.

        Provide the refined section content.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            # Clean the generated refined section content
            return remove_problematic_chars(response.choices[0].message.content)
        except Exception as e:
            print(f"Error refining section {cleaned_section_name}: {str(e)}")
            return f"Error refining section {cleaned_section_name}: {str(e)}"

    def generate_compliance_matrix(self, rfp_analysis):
        """Generate a compliance matrix using the new prompt"""
        # Ensure input analysis text is cleaned
        cleaned_rfp_analysis = remove_problematic_chars(rfp_analysis)
        key_requirements_pattern = r"KEY REQUIREMENTS(.*?)DELIVERABLES"
        key_requirements = re.search(key_requirements_pattern, cleaned_rfp_analysis, re.DOTALL)
        key_requirements = key_requirements.group(1).strip() if key_requirements else ""

        prompt = f"""
        Create a comprehensive compliance matrix that maps RFP requirements to our proposal sections.

        Use the following RFP analysis to identify all requirements:
        {key_requirements}

        For each requirement:
        1. Quote the exact requirement language from the RFP
        2. Identify which proposal section(s) address this requirement
        3. Provide a brief (1-2 sentence) explanation of how our proposal addresses this requirement
        4. Indicate compliance status: "Fully Compliant", "Partially Compliant"

        Format the output as a structured markdown table with the following columns:
        | RFP Requirement | Reference | Addressing Section(s) | How Addressed | Compliance Status |

        Where "Reference" refers to the section/page number in the original RFP.

        Ensure every requirement from the KEY REQUIREMENTS section of the RFP analysis is included.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            # Clean the generated compliance matrix text
            return remove_problematic_chars(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating compliance matrix: {str(e)}")
            return "Error generating compliance matrix."

    def perform_risk_assessment(self, rfp_analysis):
        """Generate a risk assessment using the new prompt"""
        # Ensure input analysis text is cleaned
        cleaned_rfp_analysis = remove_problematic_chars(rfp_analysis)
        prompt = f"""
        Create a comprehensive risk assessment for this proposal based on the following RFP analysis:
        {cleaned_rfp_analysis}

        Identify specific risks in the following categories:

        1. TECHNICAL RISKS: Integration challenges, technology limitations, compatibility issues
        2. TIMELINE RISKS: Schedule constraints, dependencies, resource availability
        3. SCOPE RISKS: Unclear requirements, potential scope changes, feature creep
        4. CLIENT RELATIONSHIP RISKS: Communication challenges, alignment issues, expectation management
        5. DELIVERY RISKS: Quality assurance, testing limitations, deployment challenges
        6. EXTERNAL RISKS: Market conditions, regulatory issues, third-party dependencies

        For each identified risk, provide:
        1. A specific, concrete description of the risk
        2. Probability assessment (Low, Medium, High) with brief justification
        3. Impact assessment (Low, Medium, High) with brief justification
        4. Specific mitigation strategy including both preventive and contingency approaches
        5. Risk owner (which team or role should manage this risk)

        Format as a well-structured markdown table. Prioritize the top 2-3 risks in each category rather than creating an exhaustive list. Focus on risks specific to this client and project.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            # Clean the generated risk assessment text
            return remove_problematic_chars(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating risk assessment: {str(e)}")
            return "Error generating risk assessment."

    def research_client_background(self, client_name):
        """Research client background using the new prompt"""
        # Ensure client name is cleaned before sending to LLM
        cleaned_client_name = remove_problematic_chars(client_name) if client_name else ""

        prompt = f"""
        Based on the client name '{cleaned_client_name}', create a strategic client profile for proposal customization.

        The profile should include:

        1. ORGANIZATION OVERVIEW:
            - Industry position and primary business focus
            - Approximate size (employees, revenue if public)
            - Geographic presence and market focus
            - Key products or services

        2. STRATEGIC PRIORITIES:
            - Current business challenges or transformation initiatives
            - Recent technology investments or digital initiatives
            - Growth areas or new market entries
            - Corporate values or mission emphasis

        3. DECISION-MAKING CONTEXT:
            - Organizational structure relevant to this proposal
            - Likely stakeholders and their priorities
            - Previous vendor relationships or relevant partnerships
            - Procurement or decision-making approach if known

        4. TECHNOLOGY LANDSCAPE:
            - Current systems or platforms likely in use
            - Technology stack preferences if known
            - Prior implementation successes or challenges
            - Digital maturity assessment

        Focus on factual information that can be verified. Where specific details aren't available, provide industry-standard insights that would still be relevant. Include only information that would directly enhance proposal customization.

        Format the response with clear headings and concise bullet points for easy reference.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )

            # Clean the generated client background text
            return remove_problematic_chars(response.choices[0].message.content)
        except Exception as e:
            print(f"Error researching client: {str(e)}")
            return "Client background information not available."

    def evaluate_proposal_alignment(self, evaluation_criteria, proposal_sections):
        """Evaluate proposal alignment using the new prompt"""
        # Ensure input text is cleaned before sending to LLM
        cleaned_evaluation_criteria = remove_problematic_chars(evaluation_criteria)
        # Assuming proposal_sections keys are section names (already cleaned) and values are content (also cleaned)
        cleaned_proposal_sections_for_prompt = {
            remove_problematic_chars(name): remove_problematic_chars(content)
            for name, content in proposal_sections.items()
        }


        prompt = f"""
        Evaluate how effectively our proposed sections align with the evaluation criteria identified in the RFP analysis.

        RFP EVALUATION CRITERIA:
        {cleaned_evaluation_criteria}

        PROPOSED SECTIONS:
        {json.dumps(cleaned_proposal_sections_for_prompt, indent=2)} # Send cleaned sections as JSON string

        For each evaluation criterion:

        1. Identify which specific proposal section(s) address this criterion
        2. Rate our coverage as:
            - STRONG: Comprehensively addresses all aspects of the criterion
            - ADEQUATE: Addresses core requirements but could be strengthened
            - NEEDS IMPROVEMENT: Insufficient coverage or missing key elements
            - ABSENT: Not addressed in current proposal structure

        3. Provide specific, actionable recommendations to strengthen our alignment, such as:
            - Content additions or emphasis changes
            - Supporting evidence or examples to include
            - Structural improvements or section reorganization
            - Cross-references between sections to reinforce key points
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            # Clean the generated alignment assessment text
            return remove_problematic_chars(response.choices[0].message.content)
        except Exception as e:
            print(f"Error evaluating proposal alignment: {str(e)}")
            return "Error evaluating proposal alignment with RFP criteria."

    def generate_executive_summary(self, client_background, rfp_analysis, differentiators, solution_overview, client_name):
        """Generate an executive summary using the specialized prompt"""
        # Ensure all input text is cleaned before sending to LLM
        cleaned_client_background = remove_problematic_chars(client_background) if client_background else ""
        cleaned_rfp_analysis = remove_problematic_chars(rfp_analysis)
        cleaned_differentiators = remove_problematic_chars(differentiators) if differentiators else ""
        cleaned_solution_overview = remove_problematic_chars(solution_overview) if solution_overview else ""
        cleaned_client_name = remove_problematic_chars(client_name) if client_name else ""


        prompt = f"""
        Create a compelling Executive Summary for this proposal based on the following inputs:

        CLIENT BACKGROUND:
        {cleaned_client_background}

        RFP ANALYSIS:
        {cleaned_rfp_analysis}

        KEY DIFFERENTIATORS:
        {cleaned_differentiators}

        SOLUTION OVERVIEW:
        {cleaned_solution_overview}

        Your Executive Summary should:

        1. Open with a concise statement acknowledging the client's specific needs and challenges
        2. Present our understanding of their primary objectives in pursuing this project
        3. Outline our proposed approach at a high level (without technical detail)
        4. Highlight 2-3 key differentiators that make our solution uniquely valuable
        5. Reference our relevant experience and qualifications specifically relevant to their needs
        6. Close with a compelling value proposition that addresses their business outcomes

        Keep the Executive Summary to approximately 500 words using clear, confident language that demonstrates both understanding and expertise. Avoid generic claims and focus on client-specific value. Use minimal formatting - short paragraphs with occasional bold text for emphasis.

        The Executive Summary should stand alone if separated from the full proposal while compelling the reader to continue.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )

            # Clean the generated executive summary text
            return remove_problematic_chars(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating executive summary: {str(e)}")
            return f"Error generating executive summary: {str(e)}"

    def generate_full_proposal(self, rfp_text, client_name=None, company_info=None, template_sections=None):
        """Generate a full proposal with checks for KB initialization."""

        # --- ADDED CHECK ---
        # Check if the Knowledge Base is initialized and has the required methods
        if not self.kb or not hasattr(self.kb, 'multi_hop_search') or not hasattr(self.kb, 'extract_pricing_from_kb'):
            st.error("Knowledge Base is not properly initialized within the Proposal Generator. Cannot generate full proposal.")
            # Return an error structure consistent with the expected output
            return {
                "analysis": "Error: Knowledge Base not initialized.",
                "sections": {},
                "client_background": "Client background not available due to KB error.",
                "differentiators": company_info.get("differentiators", "") if company_info else "",
                "required_sections": template_sections or [],
                "client_name": remove_problematic_chars(client_name) if client_name else None
            }
        # --- END CHECK ---

        print("Analyzing RFP...")
        # Clean RFP text before analysis
        cleaned_rfp_text = remove_problematic_chars(rfp_text)
        rfp_analysis = self.analyze_rfp(cleaned_rfp_text) # Analysis result is cleaned by the method

        if template_sections:
            # Ensure template sections are cleaned
            required_sections = [remove_problematic_chars(s) for s in template_sections]
        else:
            # extract_required_sections uses cleaned analysis and returns cleaned sections
            required_sections = self.extract_required_sections(rfp_analysis)
            if not required_sections: # Fallback if LLM fails extraction or returns empty
                rfp_doc_sections = extract_sections_from_rfp(cleaned_rfp_text)
                required_sections = [remove_problematic_chars(s) for s in rfp_doc_sections.keys()] if rfp_doc_sections else ["Introduction", "Proposed Solution", "Pricing", "Conclusion"]
                st.warning(f"Could not extract specific required sections from RFP Analysis. Using sections: {', '.join(required_sections)}")


        # Clean client name and company info before research/use
        cleaned_client_name = remove_problematic_chars(client_name) if client_name else None
        cleaned_company_info = {
            "name": remove_problematic_chars(company_info.get("name", "")) if company_info else "",
            "differentiators": remove_problematic_chars(company_info.get("differentiators", "")) if company_info else ""
        } if company_info else {}


        if cleaned_client_name:
            # research_client_background returns cleaned background
            client_background = self.research_client_background(cleaned_client_name)
        else:
            client_background = "Client background not provided."

        differentiators = cleaned_company_info.get("differentiators", "Company differentiators not provided.")


        criteria_pattern = r"EVALUATION CRITERIA(.*?)CLIENT PAIN POINTS"
        # Use cleaned rfp_analysis for pattern matching
        evaluation_criteria_match = re.search(criteria_pattern, rfp_analysis, re.DOTALL)
        # evaluation_criteria is cleaned after extraction
        evaluation_criteria = remove_problematic_chars(evaluation_criteria_match.group(1).strip()) if evaluation_criteria_match else "Evaluation criteria not specified."

        proposal_sections = {}
        # Extract sections from the cleaned RFP text once before the loop
        rfp_sections_content_map = extract_sections_from_rfp(cleaned_rfp_text)

        for section_name in required_sections: # required_sections are already cleaned
            print(f"Generating section: {section_name}")

            # Find corresponding RFP section content (case-insensitive matching)
            rfp_section_content_for_llm = next((content for rfp_sec_name, content in rfp_sections_content_map.items() if section_name.lower() in rfp_sec_name.lower() or rfp_sec_name.lower() in section_name.lower()), "")
            # Content is already cleaned by extract_sections_from_rfp

            cleaned_rfp_section_content = remove_problematic_chars(rfp_section_content_for_llm) if rfp_section_content_for_llm else ""
            expanded_query = expand_query(section_name + " " + cleaned_rfp_section_content)

            # --- ADDED TRY-EXCEPT around KB search ---
            relevant_kb_content = [] # Default to empty list
            try:
                # Assuming self.kb was validated at the start of the method
                relevant_kb_content = self.kb.multi_hop_search(expanded_query, k=3) # multi_hop_search returns cleaned content
            except Exception as kb_error:
                st.error(f"Error searching Knowledge Base for section '{section_name}': {kb_error}")
                # Continue generation with empty KB content
            # --- END TRY-EXCEPT ---

            # Call generate_section (which now also has KB checks for pricing)
            # All inputs passed here should be cleaned versions
            proposal_sections[section_name] = self.generate_section(
                section_name,           # Cleaned
                rfp_analysis,           # Cleaned
                cleaned_rfp_section_content, # Cleaned
                client_background,      # Cleaned
                differentiators,        # Cleaned
                evaluation_criteria,    # Cleaned
                relevant_kb_content,    # Contains cleaned content
                cleaned_client_name     # Cleaned
            )

        # Generate Executive Summary if needed
        # Check against cleaned section names in the generated proposal_sections dictionary
        if "Executive Summary" not in proposal_sections and cleaned_client_name:
            print("Generating Executive Summary...")

            section_highlights = ""
            key_sections_for_summary = ["Approach", "Methodology", "Solution", "Benefits", "Implementation"]
            for summary_key_sec in key_sections_for_summary:
                # Match cleaned section names from the generated proposal
                matching_gen_section = next((s_name for s_name in proposal_sections.keys() if summary_key_sec.lower() in s_name.lower()), None)
                if matching_gen_section:
                    # Use cleaned proposal section content for highlights
                    content_preview = remove_problematic_chars(proposal_sections[matching_gen_section])[:200] + "..."
                    section_highlights += f"## {matching_gen_section} Preview\n{content_preview}\n\n"

            # Ensure section_highlights is cleaned (though composed from cleaned parts)
            cleaned_section_highlights = remove_problematic_chars(section_highlights)

            # Generate the executive summary using cleaned inputs
            try:
                # generate_executive_summary handles cleaning internally now
                exec_summary_content = self.generate_executive_summary(
                     client_background,     # Cleaned
                     rfp_analysis,          # Cleaned
                     differentiators,       # Cleaned
                     cleaned_section_highlights, # Cleaned overview
                     cleaned_client_name    # Cleaned
                )
                proposal_sections["Executive Summary"] = exec_summary_content # Result is cleaned by generate_executive_summary
            except Exception as e:
                 print(f"Error generating Executive Summary: {str(e)}")
                 proposal_sections["Executive Summary"] = "Error generating Executive Summary." # Add placeholder on error

        # Final structure uses cleaned data
        return {
            "analysis": rfp_analysis,
            "sections": proposal_sections,
            "client_background": client_background,
            "differentiators": differentiators,
            "required_sections": required_sections,
            "client_name": cleaned_client_name
        }


    def perform_quality_assurance(self, proposal_sections, rfp_analysis):
        """Perform quality assurance checks on the proposal"""
        # Clean proposal sections before sending to LLM for QA
        cleaned_proposal_sections = {remove_problematic_chars(name): remove_problematic_chars(content) for name, content in proposal_sections.items()}

        prompt = f"""
        # QUALITY ASSURANCE CHECK

        ## PROPOSAL SECTIONS
        {json.dumps(cleaned_proposal_sections, indent=2)}

        ## RFP ANALYSIS
        {remove_problematic_chars(rfp_analysis)} # Clean RFP analysis too

        ## QUALITY ASSURANCE INSTRUCTIONS
        Perform comprehensive quality assurance checks on the proposal sections:

        1. LANGUAGE TONE:
            - Evaluate if the tone is professional and confident
            - Check for overly technical language that might confuse the client
            - Identify any overly casual or informal language

        2. GRAMMAR AND SPELLING:
            - Identify any grammatical errors
            - Check for spelling mistakes
            - Verify consistency in verb tenses and subject-verb agreement

        3. COMPLIANCE WITH RFP GUIDELINES:
            - Verify that all sections address the RFP requirements
            - Check if the proposal follows the structure requested in the RFP
            - Ensure all mandatory elements from the RFP are included

        4. CONTENT QUALITY:
            - Evaluate if claims are supported with evidence
            - Check for vague statements that should be more specific
            - Identify any sections that could benefit from additional details

        Provide specific feedback for each section, including:
        - Exact location of the issue
        - Description of the problem
        - Suggested improvement

        Format the output as a structured markdown report with the following sections:
        ## Overall Quality Score (1-10)
        ## Tone Assessment
        ## Grammar and Spelling Issues
        ## Compliance with RFP Guidelines
        ## Content Quality Feedback
        ## Actionable Improvements
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            # Clean the generated QA text
            return remove_problematic_chars(response.choices[0].message.content)
        except Exception as e:
            print(f"Error performing quality assurance: {str(e)}")
            return "Error performing quality assurance."

    def generate_advanced_analysis(self, proposal_data, rfp_analysis, internal_capabilities, client_name):
        """Generate advanced analysis without executive summary"""
        analysis_results = {}

        # Clean inputs before passing to generation functions
        cleaned_rfp_analysis = remove_problematic_chars(rfp_analysis)
        # Clean proposal section names (keys) for sending to LLM
        cleaned_proposal_sections_keys = [remove_problematic_chars(name) for name in proposal_data["sections"].keys()]
        cleaned_internal_capabilities = {
            key: [remove_problematic_chars(item) for item in value]
            for key, value in internal_capabilities.items()
        }
        cleaned_client_name = remove_problematic_chars(client_name) if client_name else ""

        compliance_matrix = self.generate_compliance_matrix(cleaned_rfp_analysis)
        analysis_results["compliance_matrix"] = compliance_matrix

        risk_assessment = self.perform_risk_assessment(cleaned_rfp_analysis)
        analysis_results["risk_assessment"] = risk_assessment

        criteria_pattern = r"EVALUATION CRITERIA(.*?)CLIENT PAIN POINTS"
        evaluation_criteria = re.search(criteria_pattern, cleaned_rfp_analysis, re.DOTALL)
        evaluation_criteria = evaluation_criteria.group(1).strip() if evaluation_criteria else "Evaluation criteria not specified."
        cleaned_evaluation_criteria = remove_problematic_chars(evaluation_criteria)


        alignment_assessment = self.evaluate_proposal_alignment(
            cleaned_evaluation_criteria,
            # Pass the dictionary of cleaned section names and content for alignment evaluation
            {remove_problematic_chars(name): remove_problematic_chars(content) for name, content in proposal_data["sections"].items()}
        )
        analysis_results["alignment_assessment"] = alignment_assessment

        compliance_assessment = self.assess_compliance(cleaned_rfp_analysis, cleaned_internal_capabilities)
        analysis_results["compliance_assessment"] = compliance_assessment

        return analysis_results

    def analyze_vendor_proposal(self, vendor_proposal_text, rfp_analysis, client_name, scoring_system):
        """Analyze vendor proposal against RFP requirements with detailed factual comparison"""
        # Clean input texts before analysis
        cleaned_vendor_proposal_text = remove_problematic_chars(vendor_proposal_text)
        cleaned_rfp_analysis = remove_problematic_chars(rfp_analysis)
        cleaned_client_name = remove_problematic_chars(client_name) if client_name else ""

        # Extract specific RFP requirements for comparison
        weighted_criteria = self.extract_weighted_criteria(cleaned_rfp_analysis)

         # Format scoring metrics and weights from config for the prompt
        # Use the metrics from the scoring_system passed in (which could be dynamic)
        scoring_metrics_info = "\n".join([f"- {metric.replace('_', ' ').title()}" # Only include metric name in prompt, not dynamic weight
                                            for metric in scoring_system['weighting'].keys()])

        # Generate analysis prompt with detailed instructions
        analysis_prompt = f"""
        # DETAILED VENDOR PROPOSAL ANALYSIS

        ## ANALYSIS INSTRUCTIONS:
        1. Perform a comprehensive analysis of the vendor proposal against the provided RFP requirements.
        2. Evaluate the proposal based on the defined scoring metrics.
        3. For each scoring metric listed below, provide a score out of 100 based on your detailed analysis.
        4. Provide specific examples from both the RFP and proposal to support your analysis.
        5. Format your response with clear headings for each analysis category and clearly state the score for each metric using the format "**[Metric Name] Score: [Score]/100**".

        ## SCORING METRICS TO EVALUATE (Score each out of 100):
        {scoring_metrics_info}


        ## RFP REQUIREMENTS:
        {cleaned_rfp_analysis} # Use cleaned RFP analysis

        ## VENDOR PROPOSAL:
        {cleaned_vendor_proposal_text} # Use cleaned vendor text

         ## ANALYSIS FORMAT:
        ### Overall Score (0-100)
        ### Requirement Matching:
        - Fully Addressed Requirements
        - Partially Addressed Requirements
        - Unaddressed Requirements
        ### Compliance Assessment:
        - Met Requirements
        - Partially Met Requirements
        - Unmet Requirements
        ### Quality Evaluation:
        - Strengths
        - Weaknesses
        ### Alignment with Client Priorities:
        - Well-Aligned Aspects
        - Misaligned Aspects
        ### Risk Assessment:
        - Identified Risks
        - Mitigation Strategies
        ### Sentiment Analysis:
        - Tone assessment (positive, neutral, negative)
        - Confidence level of the vendor
        ### Comparative Analysis:
        - How this proposal compares to typical industry standards
        - Competitive advantages/disadvantages

        Provide specific page/section references from the proposal for each assessment point.
        Calculate an overall score based on the weighted metrics.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", # Consider GPT-4 for potentially better scoring consistency
                messages=[
                    {"role": "system", "content": "You are an expert proposal evaluator providing detailed analysis and scoring."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.1 # Lower temperature for more factual and consistent scoring
            )
            analysis_text = response.choices[0].message.content

            # Clean the generated analysis text
            cleaned_analysis_text = remove_problematic_chars(analysis_text)

            return cleaned_analysis_text
        except Exception as e:
            print(f"Error analyzing vendor proposal: {str(e)}")
            return f"Error analyzing vendor proposal: {str(e)}\n\nPrompt:\n{analysis_prompt}" # Return prompt on error for debugging


    def calculate_weighted_score(self, analysis_text: str, scoring_system: Dict) -> Tuple[Optional[float], Dict[str, Optional[int]], Optional[str]]:
        """
        Parses vendor analysis text to extract scores for configured metrics,
        calculates the weighted score, and determines the grade.
        Updated regex to be more flexible with LLM output variations.

        Args:
            analysis_text: The text output from analyze_vendor_proposal.
            scoring_system: The scoring configuration dictionary, potentially with dynamic weights.

        Returns:
            A tuple containing:
            - The total weighted score (float) or None if calculation fails.
            - A dictionary of individual metric scores (str: int) or None if not found.
            - The calculated grade (str) based on the score, or None.
        """
        # Ensure analysis text is cleaned before parsing
        cleaned_analysis_text = remove_problematic_chars(analysis_text)

        weights = scoring_system.get('weighting', {})
        grading_scale = scoring_system.get('grading_scale', {})
        individual_scores = {}
        total_weighted_score = 0.0
        total_weight_sum = sum(weights.values()) # Calculate the sum of weights provided

        # Define regex patterns based on the metrics provided in the scoring_system
        for metric in weights.keys(): # Use the keys from the provided weights
            # Create a user-friendly metric name for the regex (e.g., "requirement_match" -> "Requirement Match")
            metric_name_formatted = metric.replace('_', ' ').title()
            # Updated regex: Look for the formatted metric name, followed by anything (non-greedy),
            # then capture either digits (\d+) or "N/A". This is more robust to variations
            # in the LLM's output format after the metric name.
            pattern = re.compile(rf"{re.escape(metric_name_formatted)}.*?(\d+|N/A)", re.IGNORECASE | re.DOTALL)
            match = pattern.search(cleaned_analysis_text) # Search in cleaned text

            if match:
                score_str = match.group(1)
                if score_str.upper() == 'N/A':
                    score = None # Represent N/A as None
                else:
                    try:
                        score = int(score_str)
                        # Ensure score is within 0-100 range if it's a number
                        score = max(0, min(100, score))
                    except ValueError:
                        score = None # Handle cases where captured text isn't a valid integer

                individual_scores[metric] = score

                # Only include valid numerical scores in the weighted calculation
                if score is not None:
                    # Multiply the individual score (out of 100) by its weight
                    total_weighted_score += score * weights[metric]
                print(f"Found score for {metric}: {score_str} -> {score}, weight: {weights.get(metric, 'N/A')}") # Debug print
            else:
                individual_scores[metric] = None
                print(f"Could not find score for {metric}") # Debug print

        # Normalize the total weighted score if the total weight sum is not 1 or 100
        # If weights sum to 100, this effectively scales the score to 0-100
        # If weights sum to 1, the score is already out of 100 conceptually
        # If weights sum to something else, normalize by the sum.
        final_score_raw = total_weighted_score
        # Only normalize if there's a positive total weight
        final_score_for_grading = (final_score_raw / total_weight_sum) if total_weight_sum > 0 else 0
        # Cap the score at 100 for grading purposes, even if raw calculation exceeds it
        final_score_for_grading = min(final_score_for_grading, 100)
        # Ensure score is not negative
        final_score_for_grading = max(0, final_score_for_grading)


        print(f"Raw Weighted Score: {final_score_raw}, Score for Grading (Normalized): {final_score_for_grading:.2f}, Total Weight Sum: {total_weight_sum}") # Debug print

        # Determine grade
        grade = "N/A"
        # Sort grading scale by the lower bound in descending order to ensure correct grade assignment
        sorted_grading_scale = sorted(grading_scale.items(), key=lambda item: item[1][0], reverse=True)
        for grade_name, score_range in sorted_grading_scale:
            # Ensure score_range has two elements and they are numbers
            if isinstance(score_range, list) and len(score_range) == 2 and all(isinstance(s, (int, float)) for s in score_range):
                if score_range[0] <= final_score_for_grading <= score_range[1]:
                    grade = grade_name.title()
                    break
            else:
                print(f"Warning: Invalid grading scale format for '{grade_name}': {score_range}") # Debug print


        print(f"Calculated Grade: {grade}") # Debug print

        # Return the normalized score for display
        return final_score_for_grading, individual_scores, grade


    def identify_gaps_and_risks(self, vendor_proposal_text, rfp_requirements):
        """Use machine learning to identify gaps and risks in vendor responses"""
        # Clean input texts before processing
        cleaned_vendor_proposal_text = remove_problematic_chars(vendor_proposal_text)
        cleaned_rfp_requirements = remove_problematic_chars(rfp_requirements)

        try:
            # Vectorize text
            documents = [cleaned_rfp_requirements, cleaned_vendor_proposal_text]
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(documents)

            # Calculate similarity
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            similarity_score = similarity_matrix[0][0] # Get the single similarity value

            gaps = []
            if similarity_score < 0.7: # Threshold for identifying gaps
                gaps.append(f"Potential low coverage of key requirements (Similarity Score: {similarity_score:.2f})")
            if similarity_score < 0.5:
                gaps.append("Potential mismatch in proposed solutions compared to requirements")

            # Basic keyword-based risk identification (can be expanded)
            risks = []
            risk_keywords = ["unable to", "cannot commit", "significant challenge", "out of scope", "additional cost", "dependency on client"]
            # Iterate through the vendor proposal text to find occurrences of risk keywords
            # This is a simple approach and could be improved with NLP techniques
            cleaned_vendor_text_lower = cleaned_vendor_proposal_text.lower() # Use cleaned text for keyword search
            for keyword in risk_keywords:
                # Use re.findall to find all occurrences, case-insensitive
                if re.search(r'\b' + re.escape(keyword) + r'\b', cleaned_vendor_text_lower):
                    risks.append(f"Potential risk identified related to keyword: '{keyword}'")

            if similarity_score < 0.5:
                risks.append("High risk of non-compliance due to low overall similarity")

            # Ensure extracted gaps and risks strings are cleaned
            cleaned_gaps = [remove_problematic_chars(g) for g in gaps]
            cleaned_risks = [remove_problematic_chars(r) for r in risks]

            return cleaned_gaps, cleaned_risks
        except Exception as e:
            print(f"Error identifying gaps and risks: {str(e)}")
            return [], []

    def generate_scoring_analysis(self, vendor_analyses):
        """Generate comprehensive scoring analysis for multiple vendor proposals"""
        scores = []
        # Clean vendor analyses text before processing
        cleaned_vendor_analyses = [remove_problematic_chars(analysis) for analysis in vendor_analyses]

        for analysis in cleaned_vendor_analyses:
            try:
                # This method is currently not used in the UI tabs provided.
                # If it were, it would need to be updated to handle potentially
                # different scoring metrics/weights per vendor analysis if
                # analyses were done with different configurations.
                # For now, keeping it as is based on the original code.
                score_match = re.search(r"match\s*score\s*:\s*(\d+)", analysis, re.IGNORECASE)
                if score_match:
                    score = int(score_match.group(1))
                    scores.append(score)
            except:
                scores.append(0)

        if not scores:
            return "No scores found for analysis."

        # Calculate statistics
        avg_score = sum(scores) / len(scores)
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0

        # Generate analysis prompt
        prompt = f"""
        # VENDOR PROPOSAL SCORING ANALYSIS

        Analyze the following scores from vendor proposals:

        Scores: {', '.join(map(str, scores))}

        Calculate:
        - Average Score: {avg_score:.1f}
        - Maximum Score: {max_score}
        - Minimum Score: {min_score}

        Provide insights into:
        - How vendors performed against each other
        - Which vendors demonstrated superior alignment
        - Common strengths across proposals
        - Recurring weaknesses or gaps
        - Recommendations for vendor selection based on scores

        Format your response with clear headings and bullet points.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            # Clean the generated scoring analysis text
            return remove_problematic_chars(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating scoring analysis: {str(e)}")
            return f"Error generating scoring analysis: {str(e)}"
        
    def generate_comprehensive_sow_analysis(self, rfp_text, client_strategic_goals=None):
        """Generate comprehensive SOW analysis including all components"""
        
        sow_extractor = EnhancedSOWExtractor(self.client)
        
        # Step 1: Extract complete requirements
        print("Extracting comprehensive requirements...")
        requirements = sow_extractor.extract_complete_requirements(rfp_text)
        
        # Step 2: Structure the SOW
        print("Structuring scope of work...")
        rfp_analysis = self.analyze_rfp(rfp_text)
        sow_structure = sow_extractor.structure_scope_of_work(requirements, rfp_analysis)
        
        # Step 3: Extract bill of quantities
        print("Extracting bill of quantities...")
        bill_of_quantities = sow_extractor.extract_bill_of_quantities(sow_structure, rfp_text)
        
        # Step 4: Generate strategic executive summary
        print("Generating strategic executive summary...")
        if not client_strategic_goals:
            # Extract strategic context from RFP if not provided
            goals_pattern = r"(strategic|goal|objective|priority|vision|mission)"
            strategic_context = "\n".join([line for line in rfp_text.split('\n') 
                                         if any(keyword in line.lower() for keyword in goals_pattern.split('|'))])
            client_strategic_goals = strategic_context or "Strategic goals to be defined based on RFP context"
        
        executive_summary = sow_extractor.generate_executive_summary_with_sow(
            sow_structure, bill_of_quantities, client_strategic_goals, rfp_analysis
        )
        
        return {
            "comprehensive_requirements": requirements,
            "structured_sow": sow_structure,
            "bill_of_quantities": bill_of_quantities,
            "strategic_executive_summary": executive_summary,
            "rfp_analysis": rfp_analysis
        }
        