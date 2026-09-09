-- ==============================================================================
-- E-Commerce Data Analytics - Exploratory SQL Queries
-- ==============================================================================

-- 1. Análise de Faturação por Faixa Etária
SELECT 
    CASE 
        WHEN c.Age < 25 THEN '1. Sub 25'
        WHEN c.Age BETWEEN 25 AND 35 THEN '2. 25-35'
        WHEN c.Age BETWEEN 36 AND 50 THEN '3. 36-50'
        ELSE '4. Mais de 50' 
    END AS Faixa_Etaria,
    COUNT(DISTINCT o.OrderID) AS Total_Pedidos,
    SUM(o.Quantity * p.Price) AS Receita_Total,
    ROUND(SUM(o.Quantity * p.Price) / COUNT(DISTINCT o.OrderID), 2) AS Ticket_Medio
FROM bi_orders o
JOIN bi_customers c ON o.CustomerID = c.CustomerID
JOIN bi_products p ON o.ProductID = p.ProductID
GROUP BY 1
ORDER BY Receita_Total DESC;

-- 2. Auditoria de Integridade Referencial (Verificar Clientes Órfãos)

SELECT 
    o.CustomerID AS ID_Faltante,
    COUNT(o.OrderID) AS Pedidos_Afetados,
    SUM(o.Quantity * p.Price) AS Receita_Em_Risco
FROM bi_orders o
LEFT JOIN bi_customers c ON o.CustomerID = c.CustomerID
JOIN bi_products p ON o.ProductID = p.ProductID
WHERE c.CustomerID IS NULL
GROUP BY o.CustomerID;

-- 3. Top 5 Produtos Mais Vendidos

WITH ProdutoReceita AS (
    SELECT 
        p.ProductName,
        SUM(o.Quantity * p.Price) AS Receita_Total
    FROM bi_orders o
    JOIN bi_products p ON o.ProductID = p.ProductID
    GROUP BY p.ProductName
)
SELECT 
    ProductName,
    Receita_Total,
    RANK() OVER(ORDER BY Receita_Total DESC) AS Rank_Vendas
FROM ProdutoReceita
LIMIT 5;