from src.services.favorite_service import RecommendationService

def main():
    service = RecommendationService()
    df_bundles = service.run_recommendation()
    # Possibly do more: log, or print, etc.

if __name__ == "__main__":
    main()
