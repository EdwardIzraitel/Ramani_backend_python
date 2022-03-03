import asyncio
from fastapi import FastAPI, HTTPException
import uvicorn
import aiohttp
app = FastAPI(docs_url="/api/docs", openapi_url="/api")

VALIDSORTBY = ['id', 'reads', 'likes', 'popularity']
VALIDDIRECTION = ['asc', 'desc']
cachedQueries = {}


@app.get("/api/posts")
async def get_posts(tag='', sortBy='id', direction='asc'):
    if not tag:
        raise HTTPException(
            status_code=400, detail="Tags parameter is required")
    if sortBy not in VALIDSORTBY:
        raise HTTPException(
            status_code=400, detail="sortBy parameter is invalid")
    if direction not in VALIDDIRECTION:
        raise HTTPException(400, "direction parameter is invalid")
    splitTags = tag.split(",")
    directionBool = False if direction == 'asc' else True

    finalPosts = []
    if tag not in cachedQueries:
        async with aiohttp.ClientSession() as session:
            # since I am making concurrent calls here I have to wait until they are all done to remove duplicates
            # otherwise I could do it during each call to speed things up
            fetchPostsTask = [fetch_post(currentTag, session)
                              for currentTag in splitTags]
            allPosts = await asyncio.gather(*fetchPostsTask)
            finalPosts = remove_duplicates(allPosts)
            # I cache multiple tags
            # if the tag is new and it is single the caching is done in fetch_post,
            # and is updated here (update doesnt change anything)
            cachedQueries[tag] = finalPosts
    else:
        finalPosts = cachedQueries[tag]

    sortedPosts = sorted(
        finalPosts, key=lambda k: k[sortBy], reverse=directionBool)
    return {'posts': sortedPosts}


async def fetch_post(tag, session):
    url = 'https://api.hatchways.io/assessment/blog/posts?tag='+tag
    if not tag:
        return []
    if tag in cachedQueries:
        return cachedQueries[tag]
    async with session.get(url) as res:
        res = await res.json()
        # I cache individual tags here
        cachedQueries[tag] = res['posts']
        return cachedQueries[tag]


def remove_duplicates(allPosts):
    storedIds = set()
    unduplicatedPosts = []
    for posts in allPosts:
        for post in posts:
            if(post['id'] not in storedIds):
                storedIds.add(post['id'])
                unduplicatedPosts.append(post)
    return unduplicatedPosts


@app.get("/api/ping")
def root():
    return {"success": True}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=3000)
