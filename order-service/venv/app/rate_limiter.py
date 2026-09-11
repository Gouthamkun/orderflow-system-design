from app.redis_client import redis_client

RATE_LIMIT = 5
WINDOW_SECONDS = 60

RATE_LIMIT_SCRIPT = """
local current = redis.call("GET", KEYS[1])

if not current then
    redis.call("SET", KEYS[1], 1, "EX", ARGV[1])
    return 1
end

if tonumber(current) >= tonumber(ARGV[2]) then
    return 0
end

return redis.call("INCR", KEYS[1])
"""


def check_rate_limit(user_id: int) -> bool:
    key = f"rate_limit:user:{user_id}"

    result = redis_client.eval(
        RATE_LIMIT_SCRIPT,
        1,
        key,
        WINDOW_SECONDS,
        RATE_LIMIT
    )

    return result >0