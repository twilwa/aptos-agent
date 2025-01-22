# Extending Your Aptos Agent with Blockchain Query Capabilities

This guide builds upon your existing Aptos Agent, adding powerful blockchain querying features. You'll learn how to retrieve transaction details, account resources, and token balances directly from the Aptos blockchain.

## Prerequisites

1. Completed the main Aptos Agent setup from [README.md](README.md)
2. Working agent with basic functionality
3. Access to Aptos testnet (already configured if you followed the main guide)

## New Features Overview

Your enhanced Aptos Agent now includes capabilities to:
- Query specific transactions using transaction hashes
- View account resources and token balances
- Monitor blockchain state in real-time
- Track token holdings across accounts

## Implementation Details

### 1. Transaction Queries
```python
# Get details about a specific transaction
transaction = await get_transaction("0x123...abc")
```

The `get_transaction` function allows you to:
- Retrieve transaction status
- View transaction payload
- Check gas usage and fees
- See timestamp and chain version

### 2. Account Resources
```python
# View all resources associated with an account
resources = await get_account_resources("0x1234...")
```

Account resources provide:
- Token balances
- Staking information
- Module deployments
- Custom resource types

### 3. Token Balance Tracking
```python
# Check specific token balance
balance = await get_token_balance(
    address="0x1234...",
    creator_address="0x5678...",
    collection_name="MyCollection",
    token_name="MyToken"
)
```

## Using the New Features

Your agent now has synchronous wrapper functions for all these capabilities:

1. Transaction Details:
```python
result = get_transaction_sync("0x123...abc")
```

2. Account Resources:
```python
resources = get_account_resources_sync("0x1234...")
```

3. Token Balances:
```python
balance = get_token_balance_sync(
    address,
    creator_address,
    collection_name,
    token_name
)
```

## Error Handling

All new functions include robust error handling:
- Network connectivity issues
- Invalid addresses or hashes
- Rate limiting responses
- Missing resources

## Best Practices

1. **Transaction Queries**
   - Always verify transaction finality
   - Cache frequently accessed transaction data
   - Use pagination for large result sets

2. **Resource Queries**
   - Batch related resource requests
   - Monitor rate limits
   - Implement retry logic for failed requests

3. **Token Balance Checks**
   - Verify token existence before querying
   - Handle decimal places appropriately
   - Consider using indexed queries for large collections

## Next Steps

Now that your agent can query blockchain state, consider:
1. Building automated monitoring systems
2. Creating token portfolio trackers
3. Implementing transaction history analysis
4. Developing custom analytics tools

For more advanced features and detailed API documentation, visit [aptos.dev](https://aptos.dev).