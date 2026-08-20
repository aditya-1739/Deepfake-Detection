import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from bson import ObjectId
from app.api.deps import get_current_user
from app.database.connection import get_db
from app.core.security import verify_password, get_password_hash

router = APIRouter()

class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)

@router.get("/dashboard")
async def get_dashboard(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection failed")
        
    try:
        user_id = current_user["id"]
        # Counts
        total_scans = await db["predictions"].count_documents({"user_id": user_id})
        fake_scans = await db["predictions"].count_documents({"user_id": user_id, "prediction": "FAKE"})
        real_scans = await db["predictions"].count_documents({"user_id": user_id, "prediction": "REAL"})
        
        # Recent scans
        cursor = db["predictions"].find({"user_id": user_id}).sort("upload_date", -1).limit(5)
        recent_scans = await cursor.to_list(length=5)
        
        for scan in recent_scans:
            scan["id"] = str(scan["_id"])
            del scan["_id"]
            if isinstance(scan.get("upload_date"), datetime.datetime):
                scan["upload_date"] = scan["upload_date"].isoformat()
                
        return {
            "user": {
                "email": current_user["email"],
                "id": user_id
            },
            "stats": {
                "total_scans": total_scans,
                "fake_scans": fake_scans,
                "real_scans": real_scans,
                "fake_ratio": round((fake_scans / total_scans * 100), 2) if total_scans > 0 else 0.0
            },
            "recent_scans": recent_scans
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch dashboard data: {str(e)}")

@router.get("/history")
async def user_history(
    limit: int = 100,
    skip: int = 0,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection failed")
        
    try:
        cursor = db["predictions"].find({"user_id": current_user["id"]}).sort("upload_date", -1).skip(skip).limit(limit)
        predictions = await cursor.to_list(length=limit)
        
        for pred in predictions:
            pred["id"] = str(pred["_id"])
            del pred["_id"]
            if isinstance(pred.get("upload_date"), datetime.datetime):
                pred["upload_date"] = pred["upload_date"].isoformat()
                
        return predictions
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve prediction history: {str(e)}")

@router.get("/search")
async def search_history(
    q: Optional[str] = None,
    verdict: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection failed")
        
    try:
        query = {"user_id": current_user["id"]}
        if q:
            query["filename"] = {"$regex": q, "$options": "i"}
        if verdict:
            query["prediction"] = verdict.upper()
            
        cursor = db["predictions"].find(query).sort("upload_date", -1)
        predictions = await cursor.to_list(length=100)
        
        for pred in predictions:
            pred["id"] = str(pred["_id"])
            del pred["_id"]
            if isinstance(pred.get("upload_date"), datetime.datetime):
                pred["upload_date"] = pred["upload_date"].isoformat()
                
        return predictions
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Search failed: {str(e)}")

@router.get("/stats")
async def get_statistics(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection failed")
        
    try:
        user_id = current_user["id"]
        
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$prediction",
                "count": {"$sum": 1},
                "avg_confidence": {"$avg": "$confidence"}
            }}
        ]
        
        cursor = db["predictions"].aggregate(pipeline)
        results = await cursor.to_list(length=10)
        
        total_scans = 0
        fake_scans = 0
        real_scans = 0
        avg_confidence_fake = 0.0
        avg_confidence_real = 0.0
        
        for r in results:
            verdict = r["_id"]
            count = r["count"]
            avg_conf = r["avg_confidence"] or 0.0
            
            total_scans += count
            if verdict == "FAKE":
                fake_scans = count
                avg_confidence_fake = round(avg_conf, 2)
            elif verdict == "REAL":
                real_scans = count
                avg_confidence_real = round(avg_conf, 2)
                
        # Group by device
        device_pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$device",
                "count": {"$sum": 1}
            }}
        ]
        device_cursor = db["predictions"].aggregate(device_pipeline)
        device_results = await device_cursor.to_list(length=10)
        devices = {r["_id"]: r["count"] for r in device_results if r["_id"]}
        
        return {
            "total_scans": total_scans,
            "fake_scans": fake_scans,
            "real_scans": real_scans,
            "avg_confidence_fake": avg_confidence_fake,
            "avg_confidence_real": avg_confidence_real,
            "devices": devices
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch statistics: {str(e)}")

@router.post("/change-password")
async def change_password(
    data: PasswordChangeRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection failed")
        
    user = await db["users"].find_one({"_id": ObjectId(current_user["id"])})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    if not verify_password(data.current_password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password")
        
    new_hashed_password = get_password_hash(data.new_password)
    
    await db["users"].update_one(
        {"_id": ObjectId(current_user["id"])},
        {"$set": {"hashed_password": new_hashed_password}}
    )
    
    return {"success": True, "message": "Password changed successfully"}

@router.delete("")
@router.delete("/")
async def delete_account(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection failed")
        
    try:
        user_id = current_user["id"]
        # Delete user predictions
        await db["predictions"].delete_many({"user_id": user_id})
        
        # Delete user document
        result = await db["users"].delete_one({"_id": ObjectId(user_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
        return {"success": True, "message": "User account and associated predictions cascade deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete account: {str(e)}")
