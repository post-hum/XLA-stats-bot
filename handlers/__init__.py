from handlers.common import router as common_router
from handlers.stats import router as stats_router
from handlers.alerts import router as alerts_router

routers = [common_router, stats_router, alerts_router]
