from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
import uvicorn
from routers import photos, auth, private

app  = FastAPI()

app.include_router(photos.router)
app.include_router(auth.router)
app.include_router(private.router)


@app.get("/files/{filename}", tags=['Files'])
def file_by_path(filename: str):
    try:
        return FileResponse(f'E:/Web Project/Photos/{filename}')
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")
    

if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8000, reload=True)