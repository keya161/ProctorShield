'use client';

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import s1 from "@/public/s1.json";
import s2 from "@/public/s2.json";
import securityDark from "@/public/security-dark.json";
import { AnimationContainer } from "@/components/ui/animation-container";

const animationDataPaths = [
  { animation: s1, text: "Intelligent Proctoring Solutions" },
  { animation: s2, text: "Real-time Monitoring & Analysis" },
  { animation: securityDark, text: "Advanced Security Measures" },
];

export const HeroSection = () => {
  const router = useRouter();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isTextFading, setIsTextFading] = useState(false);

  // Handle animation index changes
  useEffect(() => {
    const interval = setInterval(() => {
      setIsTextFading(true);
      setTimeout(() => {
        setCurrentIndex((prevIndex) => (prevIndex + 1) % animationDataPaths.length);
        setIsTextFading(false);
      }, 500);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <section className="container w-full">
      <div className="grid place-items-center lg:max-w-screen-xl gap-8 mx-auto py-20 md:py-32">
        <div className="text-center space-y-8">
          <Badge variant="outline" className="text-sm py-2">
            <span className="mr-2 text-primary">
              <Badge>New</Badge>
            </span>
            <span> ProctorShield: The future of security is here!</span>
          </Badge>

          <div className="max-w-screen-md mx-auto text-center text-4xl md:text-6xl font-bold">
            <h1>
              Experience the power of
              <span className="text-transparent px-2 bg-gradient-to-r from-[#D247BF] to-primary bg-clip-text">
                ProctorShield
              </span>
              in action
            </h1>
          </div>

          <p className="max-w-screen-sm mx-auto text-xl text-muted-foreground">
            {`ProctorShield isn't just another security solution; it's a smart, AI-powered system that evolves with your needs.
            Protect your digital assets, enhance your security, and get real-time insights like never before.`}
          </p>

          <div className="space-y-4 md:space-y-0 md:space-x-4">
            <Button
              onClick={() => router.push("/candidate")}
              className="w-5/6 md:w-1/4 font-bold group/arrow"
            >
              Check in Candidate
              <ArrowRight className="size-5 ml-2 group-hover/arrow:translate-x-1 transition-transform" />
            </Button>

            <Button
              asChild
              variant="secondary"
              className="w-5/6 md:w-1/4 font-bold"
            >
            </Button>

            <div className="space-y-4 md:space-y-0 md:space-x-4 pt-8">
              <Button
                onClick={() => router.push("/proctor")}
                className="w-5/6 md:w-1/4 font-bold"
              >
                Check in Proctor
                <ArrowRight className="size-7 ml-2 group-hover/arrow:translate-x-1 transition-transform" />
              </Button>
            </div>
          </div>
        </div>

        <div className="relative group mt-14">
          <div className="absolute top-2 lg:-top-8 left-1/2 transform -translate-x-1/2 w-[90%] mx-auto h-24 lg:h-80 bg-primary/50 rounded-full blur-3xl"></div>
          <AnimationContainer
            animationDataPaths={animationDataPaths}
            currentIndex={currentIndex}
            isTextFading={isTextFading}
          />
          <div className="absolute bottom-0 left-0 w-full h-20 md:h-28 bg-gradient-to-b from-background/0 via-background/50 to-background rounded-lg"></div>
        </div>
      </div>
    </section>
  );
};
