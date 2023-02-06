import boto3


def createTable(dyn_resource):
    """
    Creates a DynamoDB table.
    :return: The newly created table.
    """
    table_name = 'boto3Table'
    params = {
        'TableName': table_name,
        'KeySchema': [
            {'AttributeName': 'Name', 'KeyType': 'HASH'},
        ],
        'AttributeDefinitions': [
            {'AttributeName': 'Name', 'AttributeType': 'S'},
        ],
        'ProvisionedThroughput': {
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    }
    table = dyn_resource.create_table(**params)
    print(f"Creating {table_name}...")
    table.wait_until_exists()
    print("Table created")
    return table

def addItemsToTable(table, items):
    with table.batch_writer() as batch:
        batch.put_item(Item=items[0])
        batch.put_item(Item=items[1])
        batch.put_item(Item=items[2])


    print("Items were added to the table")

def deleteItem(table, item):
    response = table.delete_item(Key = {"Name": item["Name"]})
    print(f"item with partition {item['Name']} was deleted")


def main():
    items = [
        {"Name": "Luzze John", "Email": "john@handson.cloud"},
        {"Name": "Lugugo Joshua", "Age": 26},
        {"Name": "Robert Nsamba", "Address": "kfar kama"}
    ]
    dyn_resource = boto3.resource('dynamodb')
    table = createTable(dyn_resource)
    addItemsToTable(table, items)
    deleteItem(table, items[0])
    print("Done!")

main()