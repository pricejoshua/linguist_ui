import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))
from datetime import datetime
from typing import List, Dict, Any, Optional

async def get_all_projects() -> List[Dict[str, Any]]:
    """Fetch all projects from database"""
    try:
        result = supabase.table('projects').select('*').order('created_at', desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching projects: {e}")
        return []

async def create_project(title: str, ui_language: str, target_language: str, created_by: Optional[int] = None) -> Dict[str, Any]:
    """Insert new project into database"""
    try:
        project_data = {
            'title': title,
            'ui_language': ui_language,
            'target_language': target_language,
            'created_at': datetime.utcnow().isoformat()
        }
        if created_by:
            project_data['created_by'] = created_by

        result = supabase.table('projects').insert(project_data).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        print(f"Error creating project: {e}")
        raise e

async def get_project_campaigns(project_id: int) -> List[Dict[str, Any]]:
    """Fetch campaigns for a specific project"""
    try:
        result = supabase.table('campaigns').select('*').eq('project_id', project_id).order('created_at', desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching campaigns: {e}")
        return []

async def get_all_campaigns() -> List[Dict[str, Any]]:
    """Fetch all campaigns with project info"""
    try:
        result = supabase.table('campaigns').select('*, projects(title)').order('created_at', desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching campaigns: {e}")
        return []

async def get_campaign_responses(campaign_id: int) -> List[Dict[str, Any]]:
    """Fetch responses for a specific campaign"""
    try:
        # Get questions in this campaign first
        campaign_questions = supabase.table('campaign_questions').select('question_id').eq('campaign_id', campaign_id).execute()
        question_ids = [q['question_id'] for q in campaign_questions.data] if campaign_questions.data else []

        if not question_ids:
            return []

        # Get responses for those questions
        result = supabase.table('responses').select('*, questions(input_text)').in_('question_id', question_ids).order('created_at', desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching responses: {e}")
        return []

async def get_all_responses() -> List[Dict[str, Any]]:
    """Fetch all responses with question info"""
    try:
        result = supabase.table('responses').select('*, questions(input_text)').order('created_at', desc=True).limit(100).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching responses: {e}")
        return []
