import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Import the travel orchestration agent
try:
    from Travel_Orchestration_Agent import TravelOrchestrationAgent
except Exception:
    # Fallback for direct execution if module path differs
    from .Travel_Orchestration_Agent import TravelOrchestrationAgent  # type: ignore


def main():
    """Main function to run the personalized trip planner"""
    load_dotenv()

    # Check if API key is configured
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY not found in environment variables")
        print("Please set your Gemini API key in the .env file")
        sys.exit(1)

    print("🧭 Initializing AI-Powered Trip Planner...")
    agent = TravelOrchestrationAgent()

    # Collect inputs
    if len(sys.argv) > 1:
        # Expect JSON string or path to JSON file as single arg
        arg = sys.argv[1]
        if os.path.exists(arg):
            with open(arg, "r") as f:
                preferences = json.load(f)
        else:
            try:
                preferences = json.loads(arg)
            except json.JSONDecodeError:
                print("❌ Provide trip preferences as a JSON file path or JSON string")
                sys.exit(1)
    else:
        # Interactive minimal prompt
        traveler_name = input("Traveler name: ").strip() or "Traveler"
        origin = input("Origin (city/airport code): ").strip() or "JFK"
        destination = input("Destination (city/country): ").strip() or "Tokyo"
        start_date = input("Start date (YYYY-MM-DD): ").strip() or "2025-10-10"
        end_date = input("End date (YYYY-MM-DD): ").strip() or "2025-10-17"
        budget_str = input("Total budget (number): ").strip() or "2500"
        interests_str = input("Interests (comma-separated): ").strip() or "culture,food,nightlife"
        travelers_count_str = input("Travelers count: ").strip() or "1"
        accommodation_tier = input("Accommodation tier (budget/mid/premium/luxury): ").strip() or "mid"
        pace = input("Trip pace (relaxed/balanced/packed): ").strip() or "balanced"

        try:
            budget_total = float(budget_str)
        except Exception:
            budget_total = 2500.0
        try:
            travelers_count = int(travelers_count_str)
        except Exception:
            travelers_count = 1

        preferences = {
            "traveler_name": traveler_name,
            "origin": origin,
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "budget_total": budget_total,
            "interests": [s.strip() for s in interests_str.split(",") if s.strip()],
            "travelers_count": travelers_count,
            "accommodation_tier": accommodation_tier,
            "pace": pace,
        }

    print(f"\n🗺️ Planning trip for: {preferences.get('traveler_name', 'Traveler')}")
    print("=" * 50)

    try:
        start_time = datetime.now()
        result = agent.plan_trip(preferences)
        end_time = datetime.now()

        print("\n✅ PLAN COMPLETE")
        print("=" * 50)
        print(f"⏱️  Planning Time: {(end_time - start_time).total_seconds():.2f} seconds")
        print(f"🎯 Destination: {preferences.get('destination')}")
        print(f"💵 Budget Fit Score: {result.get('budget_fit_score', 0.0):.2f}")

        memo = result.get("itinerary", {}).get("memo", "")
        if memo:
            print(f"\n📝 TRIP MEMO:\n{memo}")

        if result.get('booking_details'):
            print("\n📦 BOOKING DETAILS:")
            print("-" * 30)
            print(json.dumps(result['booking_details'], indent=2))

        if result.get('payment_receipt'):
            print("\n💳 PAYMENT RECEIPT:")
            print("-" * 30)
            print(json.dumps(result['payment_receipt'], indent=2))

        if result.get('recommendations'):
            print("\n🎯 RECOMMENDATIONS:")
            print("-" * 30)
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"{i}. {rec}")

        # Save to file
        output_file = f"trip_{preferences.get('destination','trip').replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n💾 Trip plan saved to: {output_file}")

    except Exception as e:
        print(f"❌ Error during trip planning: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()


