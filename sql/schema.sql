/*
  Project: Customer 360 Intelligence Platform
  Step: Data cleaning
  
  Logic:
    1. Create a synthetic customer_id (hash of order_id modulo 1000) to simulate repeat users.
    2. change the variable type of order_date from text to date
*/

ALTER TABLE public.retail_orders
  ADD COLUMN customer_id INTEGER,
  ALTER COLUMN order_date
    TYPE date
    USING order_date::date;

UPDATE public.retail_orders
SET customer_id = ABS(HASHTEXT(order_id::text) % 1000) + 1;