"""
WHO ICD-11 API Integration Service
Provides live synchronization with WHO ICD-11 API including TM2 and Biomedicine modules.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ICDModule(Enum):
    """ICD-11 module types"""
    TM2 = "tm2"  # Traditional Medicine Module 2
    BIOMEDICINE = "biomedicine"
    FOUNDATION = "foundation"


@dataclass
class ICDConcept:
    """ICD-11 concept representation"""
    code: str
    title: str
    definition: Optional[str]
    module: ICDModule
    parent: Optional[str] = None
    children: List[str] = None
    synonyms: List[str] = None
    last_updated: datetime = None

    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.synonyms is None:
            self.synonyms = []
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()


class WHOICDService:
    """
    WHO ICD-11 API Service with advanced caching and synchronization.
    
    Features:
    - Live API integration with WHO ICD-11
    - TM2 and Biomedicine module support
    - Intelligent caching with TTL
    - Batch processing for large datasets
    - Error handling and retry logic
    - Rate limiting compliance
    """
    
    def __init__(self, client_id: str = None, client_secret: str = None):
        self.base_url = "https://id.who.int/icd"
        self.client_id = client_id or "your_client_id_here"
        self.client_secret = client_secret or "your_client_secret_here"
        self.access_token = None
        self.token_expires = None
        self.cache = {}
        self.cache_ttl = timedelta(hours=24)  # 24-hour cache
        self.rate_limit_delay = 0.1  # 100ms between requests
        
        # Cache file paths
        self.cache_dir = Path("./cache/who_icd")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.tm2_cache_file = self.cache_dir / "tm2_concepts.json"
        self.biomedicine_cache_file = self.cache_dir / "biomedicine_concepts.json"
        self.mapping_cache_file = self.cache_dir / "namaste_icd_mappings.json"
        
        # Load existing cache
        self._load_cache()

    async def _get_access_token(self) -> str:
        """Get OAuth2 access token from WHO ICD API"""
        if self.access_token and self.token_expires and datetime.utcnow() < self.token_expires:
            return self.access_token
            
        token_url = f"{self.base_url}/oauth2/token"
        
        async with aiohttp.ClientSession() as session:
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'icdapi_access'
            }
            
            try:
                async with session.post(token_url, data=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data['access_token']
                        expires_in = token_data.get('expires_in', 3600)
                        self.token_expires = datetime.utcnow() + timedelta(seconds=expires_in - 300)  # 5min buffer
                        logger.info("Successfully obtained WHO ICD-11 access token")
                        return self.access_token
                    else:
                        logger.error(f"Failed to get access token: {response.status}")
                        # Fallback to demo token for development
                        return "demo_token"
            except Exception as e:
                logger.error(f"Error getting access token: {e}")
                return "demo_token"

    async def _make_api_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make authenticated request to WHO ICD API with retry logic"""
        token = await self._get_access_token()
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Accept-Language': 'en',
            'API-Version': 'v2'
        }
        
        for attempt in range(3):  # 3 retry attempts
            try:
                await asyncio.sleep(self.rate_limit_delay)  # Rate limiting
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 429:  # Rate limited
                            wait_time = 2 ** attempt  # Exponential backoff
                            logger.warning(f"Rate limited, waiting {wait_time}s")
                            await asyncio.sleep(wait_time)
                        else:
                            logger.error(f"API request failed: {response.status}")
                            
            except Exception as e:
                logger.error(f"API request error (attempt {attempt + 1}): {e}")
                if attempt == 2:  # Last attempt
                    return None
                await asyncio.sleep(2 ** attempt)
        
        return None

    async def fetch_tm2_concepts(self, force_refresh: bool = False) -> List[ICDConcept]:
        """Fetch Traditional Medicine Module 2 concepts"""
        cache_key = "tm2_concepts"
        
        if not force_refresh and cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.utcnow() - cached_data['timestamp'] < self.cache_ttl:
                return [ICDConcept(**concept) for concept in cached_data['concepts']]
        
        logger.info("Fetching TM2 concepts from WHO ICD-11 API...")
        concepts = []
        
        # Fetch TM2 chapter (Chapter 26)
        tm2_data = await self._make_api_request("/release/11/2023-01/mms/1435254666")
        
        if tm2_data:
            concepts.extend(await self._parse_icd_hierarchy(tm2_data, ICDModule.TM2))
            
            # Cache the results
            self.cache[cache_key] = {
                'concepts': [concept.__dict__ for concept in concepts],
                'timestamp': datetime.utcnow()
            }
            self._save_cache()
            
        return concepts

    async def fetch_biomedicine_concepts(self, force_refresh: bool = False) -> List[ICDConcept]:
        """Fetch Biomedicine concepts"""
        cache_key = "biomedicine_concepts"
        
        if not force_refresh and cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.utcnow() - cached_data['timestamp'] < self.cache_ttl:
                return [ICDConcept(**concept) for concept in cached_data['concepts']]
        
        logger.info("Fetching Biomedicine concepts from WHO ICD-11 API...")
        concepts = []
        
        # Fetch major disease categories
        categories = [
            "455013390",  # Infectious diseases
            "1630407678", # Neoplasms
            "1766440644", # Blood disorders
            "334423054",  # Mental disorders
            # Add more category IDs as needed
        ]
        
        for category_id in categories:
            category_data = await self._make_api_request(f"/release/11/2023-01/mms/{category_id}")
            if category_data:
                concepts.extend(await self._parse_icd_hierarchy(category_data, ICDModule.BIOMEDICINE))
        
        # Cache the results
        self.cache[cache_key] = {
            'concepts': [concept.__dict__ for concept in concepts],
            'timestamp': datetime.utcnow()
        }
        self._save_cache()
        
        return concepts

    async def _parse_icd_hierarchy(self, data: Dict, module: ICDModule) -> List[ICDConcept]:
        """Parse ICD hierarchy data into ICDConcept objects"""
        concepts = []
        
        def extract_concept(item: Dict, parent_code: str = None) -> ICDConcept:
            code = item.get('code', item.get('@id', '').split('/')[-1])
            title = item.get('title', {}).get('@value', 'Unknown')
            definition = item.get('definition', {}).get('@value') if item.get('definition') else None
            
            concept = ICDConcept(
                code=code,
                title=title,
                definition=definition,
                module=module,
                parent=parent_code
            )
            
            # Extract synonyms
            if 'synonym' in item:
                synonyms = item['synonym']
                if isinstance(synonyms, list):
                    concept.synonyms = [s.get('@value', '') for s in synonyms]
                else:
                    concept.synonyms = [synonyms.get('@value', '')]
            
            return concept
        
        # Process current item
        if isinstance(data, dict):
            concept = extract_concept(data)
            concepts.append(concept)
            
            # Process children
            children = data.get('child', [])
            if not isinstance(children, list):
                children = [children]
                
            for child in children:
                child_concepts = await self._parse_icd_hierarchy(child, module)
                concepts.extend(child_concepts)
                concept.children.extend([c.code for c in child_concepts])
        
        return concepts

    async def search_concepts(self, query: str, module: ICDModule = None, limit: int = 10) -> List[ICDConcept]:
        """Search ICD concepts by text query"""
        search_endpoint = "/release/11/2023-01/mms/search"
        params = {
            'q': query,
            'subtreeFilterUsesFoundationDescendants': 'false',
            'includeKeywordResult': 'true',
            'useFlexisearch': 'true',
            'flatResults': 'true'
        }
        
        if module == ICDModule.TM2:
            params['chapterFilter'] = '26'  # TM2 is Chapter 26
        
        results = await self._make_api_request(search_endpoint, params)
        concepts = []
        
        if results and 'destinationEntities' in results:
            for entity in results['destinationEntities'][:limit]:
                concept = ICDConcept(
                    code=entity.get('theCode', ''),
                    title=entity.get('title', ''),
                    definition=entity.get('definition'),
                    module=module or ICDModule.FOUNDATION
                )
                concepts.append(concept)
        
        return concepts

    async def create_namaste_icd_mapping(self, namaste_concepts: List[Dict]) -> Dict[str, str]:
        """
        Create intelligent mapping between NAMASTE codes and ICD-11 codes.
        Uses semantic similarity and keyword matching.
        """
        logger.info("Creating NAMASTE to ICD-11 mappings...")
        mappings = {}
        
        # Load TM2 concepts for mapping
        tm2_concepts = await self.fetch_tm2_concepts()
        biomedicine_concepts = await self.fetch_biomedicine_concepts()
        
        all_icd_concepts = tm2_concepts + biomedicine_concepts
        
        for namaste_concept in namaste_concepts:
            namaste_code = namaste_concept.get('code', '')
            namaste_display = namaste_concept.get('display', '')
            namaste_definition = namaste_concept.get('definition', '')
            
            # Search for best match in ICD-11
            best_match = await self._find_best_icd_match(
                namaste_display, namaste_definition, all_icd_concepts
            )
            
            if best_match:
                mappings[namaste_code] = {
                    'icd_code': best_match.code,
                    'icd_title': best_match.title,
                    'module': best_match.module.value,
                    'confidence': 0.8,  # Placeholder confidence score
                    'mapping_type': 'automatic'
                }
                
                logger.debug(f"Mapped {namaste_code} -> {best_match.code}")
        
        # Save mappings to cache
        with open(self.mapping_cache_file, 'w') as f:
            json.dump(mappings, f, indent=2, default=str)
        
        return mappings

    async def _find_best_icd_match(self, namaste_display: str, namaste_definition: str, icd_concepts: List[ICDConcept]) -> Optional[ICDConcept]:
        """Find the best matching ICD concept using semantic similarity"""
        # This is a simplified implementation - in production, use advanced NLP/ML
        query_text = f"{namaste_display} {namaste_definition}".lower()
        
        best_match = None
        best_score = 0.0
        
        for icd_concept in icd_concepts:
            icd_text = f"{icd_concept.title} {icd_concept.definition or ''}".lower()
            
            # Simple keyword matching (enhance with semantic similarity)
            common_words = set(query_text.split()) & set(icd_text.split())
            score = len(common_words) / max(len(query_text.split()), len(icd_text.split()))
            
            if score > best_score and score > 0.3:  # Minimum threshold
                best_score = score
                best_match = icd_concept
        
        return best_match

    def _load_cache(self):
        """Load cached data from disk"""
        cache_files = [
            self.tm2_cache_file,
            self.biomedicine_cache_file,
            self.mapping_cache_file
        ]
        
        for cache_file in cache_files:
            if cache_file.exists():
                try:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                        cache_key = cache_file.stem
                        self.cache[cache_key] = {
                            'concepts': data,
                            'timestamp': datetime.utcnow() - timedelta(hours=1)  # Assume 1 hour old
                        }
                except Exception as e:
                    logger.error(f"Error loading cache file {cache_file}: {e}")

    def _save_cache(self):
        """Save cache data to disk"""
        for key, data in self.cache.items():
            if 'concepts' in data:
                cache_file = self.cache_dir / f"{key}.json"
                try:
                    with open(cache_file, 'w') as f:
                        json.dump(data['concepts'], f, indent=2, default=str)
                except Exception as e:
                    logger.error(f"Error saving cache file {cache_file}: {e}")

    async def sync_all_data(self) -> Dict[str, int]:
        """Sync all WHO ICD-11 data and create mappings"""
        logger.info("Starting full WHO ICD-11 data synchronization...")
        
        results = {}
        
        # Fetch TM2 concepts
        tm2_concepts = await self.fetch_tm2_concepts(force_refresh=True)
        results['tm2_concepts'] = len(tm2_concepts)
        
        # Fetch Biomedicine concepts
        biomedicine_concepts = await self.fetch_biomedicine_concepts(force_refresh=True)
        results['biomedicine_concepts'] = len(biomedicine_concepts)
        
        # Load NAMASTE concepts (from our existing data)
        namaste_file = Path("../CodeSystem-NAMASTE.json")
        if namaste_file.exists():
            with open(namaste_file, 'r') as f:
                namaste_data = json.load(f)
                namaste_concepts = [
                    {
                        'code': concept['code'],
                        'display': concept.get('display', ''),
                        'definition': concept.get('definition', '')
                    }
                    for concept in namaste_data.get('concept', [])
                ]
                
                # Create mappings
                mappings = await self.create_namaste_icd_mapping(namaste_concepts)
                results['mappings_created'] = len(mappings)
        
        logger.info(f"Synchronization complete: {results}")
        return results


# Global service instance
who_icd_service = WHOICDService()


async def initialize_who_service():
    """Initialize WHO ICD service with data sync"""
    try:
        await who_icd_service.sync_all_data()
        logger.info("WHO ICD-11 service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize WHO ICD service: {e}")


# Utility functions for FastAPI integration
async def get_who_icd_service() -> WHOICDService:
    """Dependency injection for WHO ICD service"""
    return who_icd_service
