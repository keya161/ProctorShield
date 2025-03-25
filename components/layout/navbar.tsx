"use client";

import { ChevronsDown, Github, Menu } from "lucide-react";
import React, { useState } from "react";
import {
  Sheet,
  SheetContent,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "../ui/sheet";
import { Separator } from "../ui/separator";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "../ui/navigation-menu";
import { Button } from "../ui/button";
import Link from "next/link";
import Image from "next/image";
import { ToggleTheme } from "./toogle-theme";
import { usePathname } from "next/navigation";
import ShowcasePage from "../../app/(root)/features/showcase/page";
import TrustPage from "../../app/(root)/features/trust/page";
import CapturePage from "../../app/(root)/features/capture/page";
import { useRouter } from "next/navigation";

const routeList = [
  { href: "#testimonials", label: "Project" },
  { href: "#team", label: "Team" },
  { href: "#contact", label: "Contact" },
  { href: "#faq", label: "FAQ" },
];

const featureList = [
  {
    title: "Showcase Your Value",
    description: "Highlight how ProcSheild helps solve user problems efficiently.",
    href: "/features/showcase",
    Element: <ShowcasePage />,
  },
  {
    title: "Build Trust",
    description:
      "Leverages ProcSheild's robust features to establish trust and credibility in AI-driven security.",
    href: "/features/trust",
    Element: <TrustPage />,
  },
  {
    title: "Capture Leads",
    description:
      "Design visually appealing and strategically placed lead capture forms with ProcSheild.",
    href: "/features/capture",
    Element: <CapturePage />,
  },
];

export const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  if (pathname === "/Signin" || pathname === "/Signup" || pathname === "/candidate" || pathname === "/proctor") {
    return null;
  }
  const handleFeatureClick = (href: string) => {
    router.push(href);
  };

  return (
    <header className="shadow-inner bg-opacity-15 w-[90%] md:w-[70%] lg:w-[75%] lg:max-w-screen-xl top-5 mx-auto sticky border border-secondary z-40 rounded-2xl flex justify-between items-center p-2 bg-card">
      <Link href="/" className="font-bold text-lg flex items-center">
        ProctorShield
      </Link>

      {/* Mobile Navbar */}
      <div className="flex items-center lg:hidden">
        <Sheet open={isOpen} onOpenChange={setIsOpen}>
          <SheetTrigger asChild>
            <Menu onClick={() => setIsOpen(!isOpen)} className="cursor-pointer lg:hidden" />
          </SheetTrigger>

          <SheetContent
            side="left"
            className="flex flex-col justify-between rounded-tr-2xl rounded-br-2xl bg-card border-secondary"
          >
            <div>
              <SheetHeader className="mb-4 ml-4">
                <SheetTitle className="flex items-center">
                  <Link href="/" className="flex items-center">
                    ProcSheild
                  </Link>
                </SheetTitle>
              </SheetHeader>

              <div className="flex flex-col gap-2">
                {/* Link to Home and other routes */}
                <Button
                  key="/"
                  onClick={() => setIsOpen(false)}
                  asChild
                  variant="ghost"
                  className="justify-start text-base"
                >
                  <Link href="/">Home</Link>
                </Button>

                {/* Other Links */}
                {routeList.map(({ href, label }) => (
                  <Button
                    key={href}
                    onClick={() => setIsOpen(false)}
                    asChild
                    variant="ghost"
                    className="justify-start text-base"
                  >
                    <Link href={href}>{label}</Link>
                  </Button>
                ))}

                {/* Login Link */}
                <Button
                  key="/Signin"
                  onClick={() => setIsOpen(false)}
                  asChild
                  variant="ghost"
                  className="justify-start text-base"
                >
                  <Link href="/Signin">Login</Link>
                </Button>
              </div>
            </div>

            <SheetFooter className="flex-col sm:flex-col justify-start items-start">
              <Separator className="mb-2" />
              <ToggleTheme />
            </SheetFooter>
          </SheetContent>
        </Sheet>
      </div>

      {/* Desktop Navbar */}
      <NavigationMenu className="hidden lg:block mx-auto">
        <NavigationMenuList>
          {/* Home Link */}
          <NavigationMenuItem>
            <NavigationMenuLink asChild>
              <Link href="/" className="text-base px-2">
                Home
              </Link>
            </NavigationMenuLink>
          </NavigationMenuItem>

          {/* Features Menu */}
          <NavigationMenuItem>
            <NavigationMenuContent>
              <div className="grid w-[600px] grid-cols-2 gap-5 p-4">
                <ul className="flex flex-col gap-2">
                  {featureList.map(({ title, description, href, Element }) => (
                    <li key={title} className="rounded-md p-3 text-sm hover:bg-muted cursor-pointer" onClick={() => handleFeatureClick(href)}>
                      <p className="mb-1 font-semibold leading-none text-foreground">
                        {title}
                      </p>
                      <p className="line-clamp-2 text-muted-foreground">
                        {description}
                      </p>
                    </li>
                  ))}
                </ul>
              </div>
            </NavigationMenuContent>
          </NavigationMenuItem>

          {/* Other Route Links */}
          <NavigationMenuItem>
            {routeList.map(({ href, label }) => (
              <NavigationMenuLink key={href} asChild>
                <Link href={href} className="text-base px-2">
                  {label}
                </Link>
              </NavigationMenuLink>
            ))}

            {/* Login Link */}
            <NavigationMenuLink asChild>
              <Link href="/Signin" className="text-base px-2">
                Login
              </Link>
            </NavigationMenuLink>
          </NavigationMenuItem>
        </NavigationMenuList>
      </NavigationMenu>

      {/* GitHub Button */}
      <div className="hidden lg:flex">
        <ToggleTheme />
      </div>
    </header >
  );
};
