import { Shield, Wallet, Headphones, Award } from "lucide-react";

const features = [
  {
    icon: Shield,
    title: "100% Secure Payments",
    description: "Your money is safe with us"
  },
  {
    icon: Wallet,
    title: "Best Price Guarantee",
    description: "Find a better deal? We'll match it"
  },
  {
    icon: Headphones,
    title: "24/7 Customer Support",
    description: "We're here to help anytime"
  },
  {
    icon: Award,
    title: "Trusted by Millions",
    description: "Join our happy customers"
  }
];

export function WhyChooseUs() {
  return (
    <div className="bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4">
        <h2 className="text-center mb-8">Why Choose EaseMyTrip?</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div key={index} className="bg-white p-6 rounded-lg text-center shadow-sm hover:shadow-md transition-shadow">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Icon className="w-8 h-8 text-[#2196F3]" />
                </div>
                <h3 className="mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
