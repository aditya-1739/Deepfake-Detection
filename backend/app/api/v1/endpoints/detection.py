from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/upload")
def upload_video():
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.get("/status/{task_id}")
def get_status(task_id: str):
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.get("/result/{task_id}")
def get_result(task_id: str):
    raise HTTPException(status_code=501, detail="Not Implemented")
