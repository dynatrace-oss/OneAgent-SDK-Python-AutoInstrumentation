# docker run --name mongo -d -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=password -e MONGO_INITDB_DATABASE=test_database -p 27017:27017 mongo
import autodynatrace
import motor.motor_asyncio


def test_mongo_connection():
    uri = "mongodb://root:password@localhost:27017"
    client = motor.motor_asyncio.AsyncIOMotorClient(uri)
    db = client.test_database

    async def do_insert():
        document = {"key": "value"}
        result = await db.test_collection.insert_one(document)
        print("result %s" % repr(result.inserted_id))

    loop = client.get_io_loop()
    loop.run_until_complete(do_insert())


if __name__ == "__main__":
    test_mongo_connection()
