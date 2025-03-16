"use client";

import { Shield, Brain, Clock, Users, Award,BarChart } from "lucide-react";
import { Card } from "@/components/ui/card";
import Image from "next/image";

const features = [
  {
    icon: Shield,
    title: "Advanced Security",
    description: "Real-time AI-powered monitoring ensures exam integrity with face recognition and behavior analysis."
  },
  {
    icon: Brain,
    title: "Intelligent Detection",
    description: "Machine learning algorithms detect and prevent cheating attempts while maintaining privacy."
  },
  {
    icon: Clock,
    title: "Time Efficiency",
    description: "Automated proctoring reduces administrative overhead and enables instant incident reporting."
  },
  {
    icon: Users,
    title: "Multi-Device Support",
    description: "Seamless experience across devices with responsive design and cross-platform compatibility."
  },
  {
    icon: Award,
    title: "Gamified Experience",
    description: "Engaging reward system promotes academic integrity and positive user behavior."
  },
  {
    icon: BarChart,
    title: "Advanced Analytics",
    description: "Comprehensive insights into exam patterns, behavior trends, and performance metrics."
  }
];

export default function ShowcasePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-secondary">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-primary mb-4">
            Revolutionizing Remote Proctoring
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Guard AI combines cutting-edge artificial intelligence with user-friendly design
            to create a secure and efficient remote examination environment.
          </p>
        </div>

        {/* Hero Image */}
        <div className="relative rounded-xl overflow-hidden mb-16 shadow-2xl">
        <Image
  src="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&q=80"
  alt="AI-Powered Proctoring"
  width={1200}  
  height={800}  
  className="w-full h-[400px] object-cover"
/>
          <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-transparent" />
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {features.map((feature, index) => (
            <Card key={index} className="p-6 hover:shadow-lg transition-shadow">
              <feature.icon className="w-12 h-12 text-primary mb-4" />
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </Card>
          ))}
        </div>

        {/* Stats Section */}
        <div className="bg-card rounded-xl p-8 shadow-lg">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="text-4xl font-bold text-primary mb-2">99.9%</div>
              <div className="text-muted-foreground">Accuracy Rate</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-primary mb-2">1M+</div>
              <div className="text-muted-foreground">Exams Proctored</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-primary mb-2">500+</div>
              <div className="text-muted-foreground">Institutions Trust Us</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}