from mongo import cases_collection, raw_collection

try:
    print("MongoDB connection successful ✅")

    print("Cases count:", cases_collection.count_documents({}))
    print("Raw submissions count:", raw_collection.count_documents({}))

except Exception as e:
    print("MongoDB connection failed ❌")
    print(e)
