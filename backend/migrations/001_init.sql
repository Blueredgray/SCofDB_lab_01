-- ============================================
-- Схема базы данных маркетплейса
-- ============================================

-- Включаем расширение UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Таблица статусов заказов
CREATE TABLE IF NOT EXISTS order_statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Заполнение статусов (безопасное, с проверкой на дубликаты)
INSERT INTO order_statuses (name) VALUES 
('created'),
('paid'),
('cancelled'),
('shipped'),
('completed')
ON CONFLICT (name) DO NOTHING;

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT email_check CHECK (email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$')
);

-- Таблица заказов
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status_id INTEGER NOT NULL REFERENCES order_statuses(id) DEFAULT 1,
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT total_amount_check CHECK (total_amount >= 0)
);

-- Таблица товаров в заказе
CREATE TABLE IF NOT EXISTS order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    CONSTRAINT price_check CHECK (price >= 0),
    CONSTRAINT quantity_check CHECK (quantity > 0)
);

-- Таблица истории статусов
CREATE TABLE IF NOT EXISTS order_status_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    status_id INTEGER NOT NULL REFERENCES order_statuses(id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================================
-- ТРИГГЕРЫ
-- ==========================================================

CREATE OR REPLACE FUNCTION prevent_double_payment()
RETURNS TRIGGER AS $$ DECLARE
    paid_status_id_val INTEGER;
BEGIN
    SELECT id INTO paid_status_id_val FROM order_statuses WHERE name = 'paid';
    IF NEW.status_id = paid_status_id_val THEN
        IF EXISTS (
            SELECT 1 FROM order_status_history 
            WHERE order_id = NEW.id AND status_id = paid_status_id_val
        ) THEN
            RAISE EXCEPTION 'Order % has already been paid.', NEW.id;
        END IF;
    END IF;
    RETURN NEW;
END;
 $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_prevent_double_payment ON orders;
CREATE TRIGGER trg_prevent_double_payment
BEFORE UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION prevent_double_payment();

CREATE OR REPLACE FUNCTION log_status_change()
RETURNS TRIGGER AS $$ BEGIN
    IF (TG_OP = 'INSERT') OR (OLD.status_id IS DISTINCT FROM NEW.status_id) THEN
        INSERT INTO order_status_history (order_id, status_id, changed_at)
        VALUES (NEW.id, NEW.status_id, NOW());
    END IF;
    RETURN NEW;
END;
 $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_log_status_change ON orders;
CREATE TRIGGER trg_log_status_change
AFTER INSERT OR UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION log_status_change();