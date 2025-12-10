from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
import uvicorn
from routers import photos, auth, private, albums, admin
from routers.social import likes

app  = FastAPI()

app.include_router(photos.router)
app.include_router(auth.router)
app.include_router(private.router)
app.include_router(albums.router)
app.include_router(admin.router)
app.include_router(likes.router)


if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8000, reload=True)