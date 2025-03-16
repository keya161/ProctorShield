"use client";

import { useState } from "react";
import { Shield, Mail, Building, GraduationCap, Users, CheckCircle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
// import Image from "next/image";

const benefits = [
    {
        icon: Shield,
        title: "Behavioral Monitoring",
        description: "Analyze keystrokes, mouse movements, and activity shifts to detect anomalies."
    },
    {
        icon: Users,
        title: "Scalable Solution",
        description: "Support for unlimited concurrent examinations with zero performance impact."
    },
    {
        icon: GraduationCap,
        title: "Academic Success",
        description: "95% reduction in academic dishonesty reported by partner institutions."
    }
];

const testimonial = {
    quote: "&quot;Implementing Guard AI has revolutionized our examination process. The seamless integration and robust security features have made remote testing a breeze.&quot;",
    author: "Dr. Jennifer Martinez",
    role: "Chief Digital Officer",
    institution: "Harvard University"
};

export default function CapturePage() {
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        institution: "",
        role: "",
        studentsCount: ""
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // In a real application, this would send the data to your backend
        toast.success("Thank you for your interest! We'll be in touch shortly.", {
            description: "A member of our team will contact you within 24 hours."
        });
        setFormData({
            name: "",
            email: "",
            institution: "",
            role: "",
            studentsCount: ""
        });
    };

    return (
        <div className="min-h-screen bg-gradient-to-b from-background to-secondary">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                {/* Hero Section */}
                <div className="text-center mb-16">
                    <h1 className="text-4xl font-bold text-primary mb-4">
                        Transform Your Remote Examination Process
                    </h1>
                    <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
                        Join leading institutions worldwide in revolutionizing online assessments
                        with Guard AI&apos;s cutting-edge proctoring solution.
                    </p>
                </div>

                <div className="grid md:grid-cols-2 gap-12 items-start">
                    <div className="space-y-8">
                        <div className="relative rounded-xl overflow-hidden mb-8 shadow-2xl">


                            <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-transparent" />
                        </div>

                        {/* Benefits Cards */}
                        <div className="space-y-6">
                            {benefits.map((benefit, index) => (
                                <Card key={index} className="p-6 hover:shadow-lg transition-shadow">
                                    <div className="flex items-start space-x-4">
                                        <benefit.icon className="w-8 h-8 text-primary shrink-0" />
                                        <div>
                                            <h3 className="font-semibold mb-2">{benefit.title}</h3>
                                            <p className="text-muted-foreground">{benefit.description}</p>
                                        </div>
                                    </div>
                                </Card>
                            ))}
                        </div>

                        {/* Testimonial */}
                        <Card className="p-6 bg-primary text-primary-foreground">
                            <blockquote className="mb-4 text-lg">&quot;{testimonial.quote}&quot;</blockquote>
                            <div className="font-semibold">{testimonial.author}</div>
                            <div className="text-sm opacity-90">{testimonial.role}</div>
                            <div className="text-sm opacity-90">{testimonial.institution}</div>
                        </Card>

                    </div>

                    {/* Right Column - Contact Form */}
                    <div className="sticky top-8">
                        <Card className="p-8">
                            <h2 className="text-2xl font-bold mb-6">Get Started with Guard AI</h2>
                            <form onSubmit={handleSubmit} className="space-y-6">
                                <div className="space-y-2">
                                    <Label htmlFor="name">Full Name</Label>
                                    <Input
                                        id="name"
                                        placeholder="Dr. Jane Smith"
                                        value={formData.name}
                                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                        required
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="email">Institutional Email</Label>
                                    <Input
                                        id="email"
                                        type="email"
                                        placeholder="jane.smith@university.edu"
                                        value={formData.email}
                                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                        required
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="institution">Institution Name</Label>
                                    <Input
                                        id="institution"
                                        placeholder="University of Technology"
                                        value={formData.institution}
                                        onChange={(e) => setFormData({ ...formData, institution: e.target.value })}
                                        required
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="role">Your Role</Label>
                                    <Select
                                        value={formData.role}
                                        onValueChange={(value) => setFormData({ ...formData, role: value })}
                                    >
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select your role" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="administrator">Administrator</SelectItem>
                                            <SelectItem value="faculty">Faculty Member</SelectItem>
                                            <SelectItem value="it">IT Professional</SelectItem>
                                            <SelectItem value="other">Other</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="studentsCount">Number of Students</Label>
                                    <Select
                                        value={formData.studentsCount}
                                        onValueChange={(value) => setFormData({ ...formData, studentsCount: value })}
                                    >
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select student count" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="<1000">Less than 1,000</SelectItem>
                                            <SelectItem value="1000-5000">1,000 - 5,000</SelectItem>
                                            <SelectItem value="5000-10000">5,000 - 10,000</SelectItem>
                                            <SelectItem value="10000+">More than 10,000</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <Button type="submit" className="w-full">
                                    Request Demo
                                </Button>

                                <p className="text-sm text-muted-foreground text-center">
                                    <CheckCircle className="inline-block w-4 h-4 mr-1" />
                                    Your information is secure and will never be shared
                                </p>
                            </form>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
}