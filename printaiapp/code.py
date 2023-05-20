    
    # orders_url = 'https://api.printful.com/orders'
    # orders_response = requests.post(orders_url, headers=headers, json=order)
    # response_data = orders_response.json()
    # print('_______order______')
    # print(order)
    # print('_______response______')
    # print(response_data)  # print the response JSON data
    # print('_______id______')
    # # print(response_data['result']['id'])  # print the order ID
    
    # # Get the order IDs and statuses from the response
    # print('______________________________________h___________')
    
    # print(type(orders_response.json()))
    
    # orders_response = requests.get(orders_url, headers=headers)

    # # Get the order IDs and statuses from the response
    # orders = orders_response.json()['result']
    # order_ids = []
    # order_statuses = []

    # for order in orders:
    #     order_id = order['id']
    #     order_status = order['status']
    #     order_ids.append(order_id)
    #     order_statuses.append(order_status)

    # # Return a JSON response containing the order IDs and statuses
    # return jsonify({'order_ids': order_ids, 'statuses': order_statuses})