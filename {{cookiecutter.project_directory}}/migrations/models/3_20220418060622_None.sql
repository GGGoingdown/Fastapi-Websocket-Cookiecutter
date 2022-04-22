-- upgrade --
CREATE TABLE IF NOT EXISTS "roles" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(11) NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_roles_name_3e8175" ON "roles" ("name");
COMMENT ON COLUMN "roles"."name" IS 'SUPER_ADMIN: SUPER_ADMIN\nADMIN: ADMIN\nGUEST: GUEST';
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "email" VARCHAR(50) NOT NULL UNIQUE,
    "password_hash" VARCHAR(128) NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT False,
    "is_admin" BOOL NOT NULL  DEFAULT False
);
CREATE INDEX IF NOT EXISTS "idx_users_email_133a6f" ON "users" ("email");
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "users_roles" (
    "users_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "role_id" UUID NOT NULL REFERENCES "roles" ("id") ON DELETE CASCADE
);
