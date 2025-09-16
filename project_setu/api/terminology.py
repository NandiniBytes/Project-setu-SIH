from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fhir.resources.bundle import Bundle
from fhir.resources.condition import Condition
from fhir.resources.operationoutcome import OperationOutcome
from fhir.resources.coding import Coding
from security.auth import verify_token

router = APIRouter()


@router.get("/CodeSystem/$lookup")
async def code_system_lookup(
    token_payload: Dict[str, Any] = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Lookup operation for CodeSystem resources.
    
    Args:
        token_payload: Decoded JWT token payload
        
    Returns:
        Placeholder response for CodeSystem lookup
    """
    return {
        "resourceType": "Parameters",
        "parameter": [
            {
                "name": "result",
                "valueBoolean": True
            },
            {
                "name": "message",
                "valueString": "CodeSystem lookup endpoint - placeholder implementation"
            },
            {
                "name": "user",
                "valueString": token_payload.get("sub", "unknown")
            }
        ]
    }


@router.get("/ConceptMap/$translate")
async def concept_map_translate(
    token_payload: Dict[str, Any] = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Translate operation for ConceptMap resources.
    
    Args:
        token_payload: Decoded JWT token payload
        
    Returns:
        Placeholder response for ConceptMap translation
    """
    return {
        "resourceType": "Parameters",
        "parameter": [
            {
                "name": "result",
                "valueBoolean": True
            },
            {
                "name": "message",
                "valueString": "ConceptMap translate endpoint - placeholder implementation"
            },
            {
                "name": "user",
                "valueString": token_payload.get("sub", "unknown")
            }
        ]
    }


@router.post("/Bundle")
async def handle_bundle(
    request: Request,
    incoming_bundle: Bundle,
    token_payload: Dict[str, Any] = Depends(verify_token)
) -> OperationOutcome:
    """
    Process and enrich a FHIR Bundle resource with NAMASTE terminology validation and ICD-11 enrichment.
    
    Args:
        request: FastAPI request object to access application state
        incoming_bundle: FHIR Bundle resource to process
        token_payload: Decoded JWT token payload
        
    Returns:
        OperationOutcome indicating success or failure
        
    Raises:
        HTTPException: If validation fails or processing errors occur
    """
    try:
        # Constants for system URIs
        NAMASTE_SYSTEM = "http://ayush.gov.in/fhir/CodeSystem/NAMASTE"
        ICD11_SYSTEM = "http://id.who.int/icd/entity"
        
        enriched_conditions = 0
        validation_errors = []
        
        # Validate and process each entry in the bundle
        if not incoming_bundle.entry:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bundle contains no entries"
            )
        
        for entry in incoming_bundle.entry:
            if not entry.resource:
                continue
                
            # Check if the resource is a Condition
            if entry.resource.resource_type == "Condition":
                condition = entry.resource
                
                # Validate that Condition has code and coding
                if not condition.code or not condition.code.coding:
                    validation_errors.append(
                        f"Condition {condition.id or 'unknown'} missing code.coding array"
                    )
                    continue
                
                # Check if Condition has at least one NAMASTE code
                has_namaste_code = False
                has_icd11_code = False
                namaste_codings = []
                
                for coding in condition.code.coding:
                    if coding.system == NAMASTE_SYSTEM:
                        has_namaste_code = True
                        namaste_codings.append(coding)
                    elif coding.system == ICD11_SYSTEM:
                        has_icd11_code = True
                
                # Validation: Must have at least one NAMASTE code
                if not has_namaste_code:
                    validation_errors.append(
                        f"Condition {condition.id or 'unknown'} must contain at least one NAMASTE code"
                    )
                    continue
                
                # Enrichment: Add ICD-11 codes if missing
                if not has_icd11_code:
                    # Access concept map cache from application state
                    concept_map_cache = getattr(request.app.state, 'concept_map_cache', {})
                    
                    for namaste_coding in namaste_codings:
                        namaste_code = namaste_coding.code
                        
                        # Look up translation in cache
                        if namaste_code in concept_map_cache:
                            icd11_code = concept_map_cache[namaste_code]
                            
                            # Create ICD-11 coding
                            icd11_coding = Coding(
                                system=ICD11_SYSTEM,
                                code=icd11_code,
                                display=f"ICD-11 code for {namaste_coding.display or namaste_code}"
                            )
                            
                            # Add to condition's coding array
                            condition.code.coding.append(icd11_coding)
                            enriched_conditions += 1
        
        # Check for validation errors
        if validation_errors:
            error_outcome = OperationOutcome(
                resourceType="OperationOutcome",
                issue=[
                    {
                        "severity": "error",
                        "code": "validation",
                        "details": {
                            "text": f"Bundle validation failed: {'; '.join(validation_errors)}"
                        }
                    }
                ]
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_outcome.dict()
            )
        
        # Success response
        success_outcome = OperationOutcome(
            resourceType="OperationOutcome",
            issue=[
                {
                    "severity": "information",
                    "code": "informational",
                    "details": {
                        "text": f"Bundle processed successfully. {enriched_conditions} conditions were enriched with ICD-11 codes."
                    }
                }
            ]
        )
        
        return success_outcome
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        error_outcome = OperationOutcome(
            resourceType="OperationOutcome",
            issue=[
                {
                    "severity": "error",
                    "code": "exception",
                    "details": {
                        "text": f"Unexpected error processing bundle: {str(e)}"
                    }
                }
            ]
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_outcome.dict()
        )
