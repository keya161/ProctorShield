"use client";

import { Shield, Lock, CheckCircle, Building2, FileCheck, HeartHandshake } from "lucide-react";
import { Card } from "@/components/ui/card";
import Image from "next/image";

const trustFactors = [
    {
        icon: Shield,
        title: "Military-Grade Encryption",
        description: "All data is protected with AES-256 encryption, ensuring maximum security for sensitive examination information."
    },
    {
        icon: Lock,
        title: "Privacy First",
        description: "GDPR and FERPA compliant with strict data handling protocols and user privacy protection measures."
    },
    {
        icon: CheckCircle,
        title: "Certified Security",
        description: "ISO 27001 certified with regular third-party security audits and penetration testing."
    }
];

const testimonials = [
    {
        name: "Dr. Sarah Chen",
        role: "Dean of Digital Learning",
        institution: "Stanford University",
        quote: "Guard AI has transformed our remote examination process with its robust security features and intuitive interface."
    },
    {
        name: "Prof. Michael Roberts",
        role: "Head of Assessment",
        institution: "MIT",
        quote: "The AI-driven monitoring capabilities have significantly reduced academic dishonesty while maintaining student privacy."
    },
    {
        name: "Dr. Emma Thompson",
        role: "Director of E-Learning",
        institution: "Oxford University",
        quote: "Guard AI's commitment to security and innovation has made them our trusted partner in digital assessment."
    }
];

export default function TrustPage() {
    return (
        <div className="min-h-screen bg-gradient-to-b from-background to-secondary">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                {/* Hero Section */}
                <div className="text-center mb-16">
                    <h1 className="text-4xl font-bold text-primary mb-4">
                        Trust & Security at Our Core
                    </h1>
                    <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
                        Guard AI is built on a foundation of robust security measures,
                        industry certifications, and unwavering commitment to user privacy.
                    </p>
                </div>

                {/* Security Image */}
                <div className="relative rounded-xl overflow-hidden mb-16 shadow-2xl">
                    <Image
                        src="https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80"
                        alt="Advanced Security Infrastructure"
                        width={1200}  // Specify width (adjust as needed)
                        height={800}  // Specify height (adjust as needed)
                        className="w-full h-[400px] object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-transparent" />
                </div>

                {/* Trust Factors */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
                    {trustFactors.map((factor, index) => (
                        <Card key={index} className="p-6 hover:shadow-lg transition-shadow">
                            <factor.icon className="w-12 h-12 text-primary mb-4" />
                            <h3 className="text-xl font-semibold mb-2">{factor.title}</h3>
                            <p className="text-muted-foreground">{factor.description}</p>
                        </Card>
                    ))}
                </div>

                {/* Compliance Section */}
                <div className="bg-card rounded-xl p-8 shadow-lg mb-16">
                    <h2 className="text-2xl font-bold text-center mb-8">Industry Standards & Compliance</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                        <div className="flex flex-col items-center">
                            <Building2 className="w-12 h-12 text-primary mb-2" />
                            <div className="text-center font-semibold">ISO 27001</div>
                        </div>
                        <div className="flex flex-col items-center">
                            <FileCheck className="w-12 h-12 text-primary mb-2" />
                            <div className="text-center font-semibold">GDPR</div>
                        </div>
                        <div className="flex flex-col items-center">
                            <HeartHandshake className="w-12 h-12 text-primary mb-2" />
                            <div className="text-center font-semibold">FERPA</div>
                        </div>
                        <div className="flex flex-col items-center">
                            <Shield className="w-12 h-12 text-primary mb-2" />
                            <div className="text-center font-semibold">SOC 2</div>
                        </div>
                    </div>
                </div>

                {/* Testimonials */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {testimonials.map((testimonial, index) => (
                        <Card key={index} className="p-6">
                            <blockquote className="text-muted-foreground mb-4">
                                &quot;{testimonial.quote}&quot;
                            </blockquote>

                            <div className="font-semibold">{testimonial.name}</div>
                            <div className="text-sm text-muted-foreground">{testimonial.role}</div>
                            <div className="text-sm text-primary">{testimonial.institution}</div>
                        </Card>
                    ))}
                </div>
            </div>
        </div>
    );
}