# Test Questions for RAG System

## General/Semantic Questions (RAG+LLM)
These will use the vectorstore and LLM to answer:

1. **What are the main holdings in the portfolio?**
2. **Tell me about the securities in the Garfield fund**
3. **What information do we have about trades?**
4. **Which bonds are in the portfolio?**
5. **What equity securities are being held?**
6. **Describe the custodian arrangements**
7. **What strategies are being used?**
8. **Tell me about the portfolio performance**
9. **What is the price of EJ0445951?**
10. **Which funds have the highest market value?**
11. **What trading activity has occurred?**
12. **Tell me about Berry Brand securities**
13. **What types of trades are in the system?**
14. **Which counterparties are involved in trades?**
15. **What is the allocation strategy?**



1. **How many holdings in Garfield?**
2. **Count of holdings for HoldCo 1**
3. **Number of trades for HoldCo 3**
4. **Total holdings in Garfield Fund**
5. **How many securities in HoldCo 11?**

## Sample Questions to Try
```
Q: What are the main holdings in the portfolio?
Q: Tell me about the securities we hold?
Q: What equity trades have been made?
Q: Describe the portfolios we manage
Q: What bonds are in our holdings?
Q: Which funds have the highest positions?
Q: What is the strategy for this portfolio?
Q: Tell me about custodian relationships
Q: What are the PL_YTD values for the funds?
Q: Which securities have the highest market value?
Q: What information is available about Garfield fund?
Q: Tell me about the trades in the system
Q: Which counterparties do we trade with?
Q: What is the total allocation across funds?
Q: Describe the types of securities we hold
```

## CSV Structure Reference

### Holdings CSV Columns
- AsOfDate: As of date
- PortfolioName: Fund/Portfolio name (Garfield, HoldCo 1, HoldCo 3, HoldCo 11, etc.)
- ShortName: Short identifier
- SecurityId: Unique security identifier
- SecurityTypeName: Bond, Equity, etc.
- SecName: Security name (e.g., "EJ0445951", "Berry Brand 4/11 Equity")
- Qty: Quantity held
- Price: Current price
- MV_Base: Market value in base currency
- PL_YTD: Profit/Loss year-to-date
- StartQty, StartPrice: Opening values
- CustodianName: Custodian (Well Prime, JP MORGAN, CITIGROUP, Goldman Sachs, etc.)
- DirectionName: Long/Short
- Strategy info: Strategy names and references

### Trades CSV Columns
- TradeTypeName: Buy/Sell
- SecurityId: Security being traded
- SecurityType: Type (Equity, Bond, etc.)
- Name: Security name
- Ticker: Ticker symbol (META, SPOT, etc.)
- TradeDate: Date of trade
- Quantity: Trade quantity
- Price: Trade price
- Principal: Principal amount
- PortfolioName: Fund executing trade (HoldCo 1, HoldCo 3, HoldCo 11, etc.)
- CustodianName: Custodian
- Counterparty: Trading counterparty (ABGS, etc.)
- AllocationRule: Allocation strategy
