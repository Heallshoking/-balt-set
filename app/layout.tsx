import type React from "react"
import type { Metadata } from "next"
import { Geist, Geist_Mono, Playfair_Display } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"

const _geist = Geist({ subsets: ["latin"] })
const _geistMono = Geist_Mono({ subsets: ["latin"] })
const _playfair = Playfair_Display({ subsets: ["latin", "cyrillic"] })

export const metadata: Metadata = {
  title: "BALT-SET — Виниловые пластинки: бесплатный предзаказ в Калининграде",
  description: "Заказывайте виниловые пластинки со всего мира. Бесплатный предзаказ, доставка из Москвы в Калининград. balt-set.ru",
  metadataBase: new URL("https://balt-set.ru"),
  openGraph: {
    title: "BALT-SET — Виниловые пластинки: бесплатный предзаказ",
    description: "Заказывайте виниловые пластинки со всего мира. Бесплатный предзаказ.",
    url: "https://balt-set.ru",
    siteName: "BALT-SET",
    locale: "ru_RU",
    type: "website",
  },
  icons: {
    icon: [
      {
        url: "/icon-light-32x32.png",
        media: "(prefers-color-scheme: light)",
      },
      {
        url: "/icon-dark-32x32.png",
        media: "(prefers-color-scheme: dark)",
      },
      {
        url: "/icon.svg",
        type: "image/svg+xml",
      },
    ],
    apple: "/apple-icon.png",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="ru">
      <body className={`font-sans antialiased`}>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
