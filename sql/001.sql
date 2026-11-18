CREATE TABLE IF NOT EXISTS pipeline_runs (
 id bigint generated always as identity primary key, started timestamptz default now(),
 finished timestamptz, status text not null, detail text
);
CREATE TABLE IF NOT EXISTS customers (
 id integer primary key, signup date not null, region text not null, channel text not null, segment text not null
);
CREATE TABLE IF NOT EXISTS products (
 id integer primary key, name text not null, category text not null, price integer check(price>0),
 cost integer check(cost>=0 and cost<=price), stock integer check(stock>=0)
);
CREATE TABLE IF NOT EXISTS orders (
 id integer primary key, customer_id integer not null references customers,
 ordered date not null, campaign_id integer, payment text not null
);
CREATE TABLE IF NOT EXISTS items (
 order_id integer references orders, product_id integer references products,
 quantity integer not null check(quantity>0), unit_price integer not null,
 unit_cost integer not null, discount integer not null check(discount between 0 and unit_price),
 primary key(order_id,product_id)
);
CREATE TABLE IF NOT EXISTS refunds (
 order_id integer primary key references orders, cents integer not null check(cents>0), refunded date not null
);
CREATE TABLE IF NOT EXISTS campaigns (
 id integer primary key, channel text not null, spend integer not null,
 impressions integer not null, clicks integer not null check(clicks<=impressions)
);
CREATE TABLE IF NOT EXISTS sessions (
 id integer primary key, customer_id integer references customers, visited date not null,
 variant text not null check(variant in ('Control','Treatment')), device text not null,
 cart boolean not null, converted boolean not null, check(not converted or cart)
);
CREATE INDEX IF NOT EXISTS orders_date ON orders(ordered);
CREATE INDEX IF NOT EXISTS orders_customer ON orders(customer_id,ordered);
CREATE INDEX IF NOT EXISTS sessions_date ON sessions(visited);
CREATE INDEX IF NOT EXISTS items_product ON items(product_id);
CREATE OR REPLACE VIEW order_facts AS
 SELECT o.id,o.customer_id,o.ordered,o.campaign_id,
 sum(i.quantity::bigint*i.unit_price) AS gross,
 sum(i.quantity::bigint*(i.unit_price-i.discount)) AS sales,
 sum(i.quantity::bigint*i.unit_cost) AS cost,
 coalesce(r.cents,0) AS refund
 FROM orders o JOIN items i ON i.order_id=o.id
 LEFT JOIN refunds r ON r.order_id=o.id GROUP BY o.id,r.cents;
