import asyncio
from fastapi import FastAPI, HTTPException
import uvicorn
import aiohttp
app = FastAPI(docs_url="/api/docs", openapi_url="/api")

VALIDSORTBY = ['id','reads','likes','popularity']
VALIDDIRECTION = ['asc','desc']

@app.get("/api/posts")
async def get_posts(tag='', sortBy='id',direction='asc'):
    if not tag: raise HTTPException(400, "Tags parameter is required")
    if sortBy not in VALIDSORTBY: raise HTTPException(400, "sortBy parameter is invalid")
    if direction not in VALIDDIRECTION: raise HTTPException(400, "direction parameter is invalid")
    splitTags = tag.split(",")
    directionBool = False if direction == 'asc' else True
    async with aiohttp.ClientSession() as session:
        getPostsTask = [fetch_post(currentTag,session) for currentTag in splitTags]
        allPosts= await asyncio.gather(*getPostsTask)
        flatAllPosts = [result for req in allPosts for result in req]
        finalPosts = remove_duplicates(flatAllPosts)
        sortedPosts = sorted(finalPosts, key = lambda k: k[sortBy],reverse=directionBool)
        return {'posts': sortedPosts}

async def fetch_post(tag, session):
    url='https://api.hatchways.io/assessment/blog/posts?tag='+tag
    async with session.get(url) as res:
        res = await res.json()
        return res['posts']

def remove_duplicates(allPosts):
    storedIds = set()
    unduplicatedPosts =[]
    for post in allPosts:
        if(post['id'] not in storedIds):
            storedIds.add(post['id'])
            unduplicatedPosts.append(post)
    return unduplicatedPosts

@app.get("/api/ping")
def root():
    return {"success":True}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=3000)