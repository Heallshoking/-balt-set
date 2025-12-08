"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Search, Disc3, Menu, Calendar, Phone, Send, MessageCircle, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { VinylModal } from "@/components/vinyl-modal"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import Image from "next/image"
import Link from "next/link"

const mockRecords = [
  {
    id: "VIN-10001",
    title: "The Dark Side of the Moon",
    artist: "Pink Floyd",
    year: 1973,
    country: "UK",
    price: 1200,
    status: "available" as const,
    image: "/pink-floyd-dark-side-album-cover.jpg",
    genre: "Прогрессивный рок",
    label: "Harvest Records",
    condition: "Отличное",
    description:
      "Эта пластинка — настоящий шедевр прогрессивного рока. Насыщенные звуки, философские тексты и невероятная атмосфера делают её обязательной к прослушиванию.",
  },
  {
    id: "VIN-10002",
    title: "Kind of Blue",
    artist: "Miles Davis",
    year: 1959,
    country: "США",
    price: 2200,
    status: "preorder" as const,
    image: "/miles-davis-kind-of-blue-inspired.png",
    genre: "Джаз",
    label: "Columbia Records",
    condition: "Near Mint",
    description:
      "Один из самых влиятельных джазовых альбомов в истории. Miles Davis создал шедевр модального джаза, который звучит свежо и современно даже спустя десятилетия.",
  },
  {
    id: "VIN-10003",
    title: "Машина Времени",
    artist: "Машина Времени",
    year: 1980,
    country: "СССР",
    price: 850,
    status: "available" as const,
    image: "/soviet-vinyl-record-cover-machine-of-time.jpg",
    genre: "Рок",
    label: "Мелодия",
    condition: "Хорошее",
    description:
      "Культовый советский рок-альбом, который стал символом эпохи. Тексты Андрея Макаревича до сих пор резонируют с слушателями.",
  },
  {
    id: "VIN-10004",
    title: "Random Access Memories",
    artist: "Daft Punk",
    year: 2013,
    country: "Франция",
    price: 1500,
    status: "reserved" as const,
    image: "/daft-punk-random-access-memories-album-cover.jpg",
    genre: "Электроника",
    label: "Columbia Records",
    condition: "Mint",
    description:
      "Современная классика электронной музыки. Daft Punk создали альбом, который объединяет ретро-звучание с современным продакшеном.",
  },
  {
    id: "VIN-10005",
    title: "Abbey Road",
    artist: "The Beatles",
    year: 1969,
    country: "UK",
    price: 1800,
    status: "reserved" as const,
    image: "/beatles-abbey-road-album-cover.jpg",
    genre: "Рок",
    label: "Apple Records",
    condition: "Near Mint",
    description:
      "Последний студийный альбом The Beatles — настоящий шедевр. От 'Come Together' до 'The End' — каждая композиция является частью музыкальной истории.",
  },
  {
    id: "VIN-10006",
    title: "Времена Года",
    artist: "Антонио Вивальди",
    year: 1978,
    country: "СССР",
    price: 650,
    status: "preorder" as const,
    image: "/vivaldi-four-seasons-classical-vinyl-record.jpg",
    genre: "Классика",
    label: "Мелодия",
    condition: "Хорошее",
    description:
      "Великолепная запись одного из самых известных произведений классической музыки. Советское издание отличается высоким качеством звука.",
  },
  {
    id: "VIN-10007",
    title: "Thriller",
    artist: "Michael Jackson",
    year: 1982,
    country: "США",
    price: 1950,
    status: "available" as const,
    image: "/michael-jackson-thriller-album-cover.png",
    genre: "Поп",
    label: "Epic Records",
    condition: "Near Mint",
    description:
      "Самый продаваемый альбом в истории музыки. Каждый трек — хит. Виниловое издание передаёт всю энергию и мощь оригинального звучания.",
  },
]

const API_URL = "http://176.98.178.109:8000/api/records"
const API_BASE = "http://176.98.178.109:8000"

type VinylRecord = {
  id: string
  article_id?: string
  title: string
  artist: string
  year: number
  country: string
  price: number
  status: "available" | "reserved" | "sold" | "preorder"
  image: string
  photo_url?: string
  genre?: string
  label?: string
  condition?: string
  description?: string
}

export default function VinylCatalog() {
  const [records, setRecords] = useState<VinylRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedRecord, setSelectedRecord] = useState<(typeof records)[0] | null>(null)
  const [showAiAssistant, setShowAiAssistant] = useState(false)
  const [aiMessage, setAiMessage] = useState("")
  const [isAiTyping, setIsAiTyping] = useState(false)
  const [searchFocused, setSearchFocused] = useState(false)
  const [showContactsDialog, setShowContactsDialog] = useState(false)
  const [showDeliveriesDialog, setShowDeliveriesDialog] = useState(false)
  const [menuSearchQuery, setMenuSearchQuery] = useState("")
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isCreatingPreorder, setIsCreatingPreorder] = useState(false)
  const [preorderSuccess, setPreorderSuccess] = useState<string | null>(null)

  const [chatMessages, setChatMessages] = useState<Array<{ role: "user" | "assistant"; content: string }>>([
    {
      role: "assistant",
      content:
        "Привет! 🎵 Я помогу найти виниловые пластинки. Спросите о любом исполнителе, альбоме или жанре. Доставка в Калининград из Москвы!",
    },
  ])
  const [chatInput, setChatInput] = useState("")
  const [isChatTyping, setIsChatTyping] = useState(false)
  const [isChatExpanded, setIsChatExpanded] = useState(false)

  const filteredRecords = searchQuery
    ? records.filter(
        (r) =>
          r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          r.artist.toLowerCase().includes(searchQuery.toLowerCase()) ||
          r.genre?.toLowerCase().includes(searchQuery.toLowerCase()),
      )
    : records

  useEffect(() => {
    async function fetchRecords() {
      try {
        const response = await fetch(API_URL, {
          method: "GET",
          headers: {
            Accept: "application/json",
          },
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()

        if (data && data.records && Array.isArray(data.records)) {
          // Преобразуем данные API в наш формат
          const formattedRecords = data.records.map((r: any) => ({
            id: r.article_id || r.id || String(Math.random()),
            article_id: r.article_id,
            title: r.title,
            artist: r.artist,
            year: r.year,
            country: r.country || "Россия",
            price: r.price,
            status:
              r.status === "🟢 Доступна"
                ? "available"
                : r.status === "🟡 Предзаказ"
                  ? "preorder"
                  : r.status === "🔴 Продана"
                    ? "sold"
                    : "available",
            image: r.photo_url || r.image || "/placeholder.svg",
            photo_url: r.photo_url,
            genre: r.genre,
            label: r.label,
            condition: r.condition,
            description: r.description,
          }))

          setRecords(formattedRecords)
        } else {
          console.log("[v0] API response format unexpected, using mock data")
          setRecords(mockRecords)
        }
      } catch (error) {
        console.log("[v0] Using mock data due to API error:", error)
        setRecords(mockRecords)
      } finally {
        setLoading(false)
      }
    }

    fetchRecords()
  }, [])

  useEffect(() => {
    if (searchQuery.length > 0 && !showAiAssistant) {
      setShowAiAssistant(true)
      generateAiResponse()
    } else if (searchQuery.length === 0) {
      setShowAiAssistant(false)
      setAiMessage("")
    }
  }, [searchQuery])

  const generateAiResponse = async () => {
    setIsAiTyping(true)
    await new Promise((resolve) => setTimeout(resolve, 800))

    const lowerQuery = searchQuery.toLowerCase()
    let response = ""

    if (filteredRecords.length === 1) {
      const record = filteredRecords[0]
      response = `Нашёл! "${record.title}" от ${record.artist} (${record.year}). ${record.description.slice(0, 120)}... Цена: ${record.price}₽`
    } else if (filteredRecords.length > 1) {
      response = `Найдено ${filteredRecords.length} пластинок по вашему запросу. Уточните исполнителя или название для более точных результатов.`
    } else if (lowerQuery.includes("джаз") || lowerQuery.includes("jazz")) {
      response = `В разделе джаза рекомендую "Kind of Blue" Майлза Дэвиса — легендарный альбом 1959 года, доступен в предзаказе!`
    } else if (lowerQuery.includes("рок") || lowerQuery.includes("rock")) {
      response = `Для любителей рока есть Pink Floyd, The Beatles, Машина Времени. Что именно ищете?`
    } else {
      response = `Ищу "${searchQuery}"... Не нашёл в каталоге, но могу оформить предзаказ! Это займёт пару секунд.`
    }

    setAiMessage(response)
    setIsAiTyping(false)
  }

  const reservedRecords = records.filter((r) => r.status === "reserved")

  const createNewPreorder = async (searchTerm: string) => {
    setIsCreatingPreorder(true)
    setPreorderSuccess(null)
    
    try {
      // Отправляем запрос на сервер для создания предзаказа
      const response = await fetch(`${API_BASE}/api/preorder`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          search_query: searchTerm,
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      
      // Создаём локальную карточку для отображения
      const newRecord: VinylRecord = {
        id: data.article_id,
        article_id: data.article_id,
        title: data.title,
        artist: data.artist,
        year: new Date().getFullYear(),
        country: "Уточняется",
        price: 0,
        status: "preorder" as const,
        image: "/placeholder.svg",
        genre: "Уточняется",
        label: "Уточняется",
        condition: "Новая",
        description: data.message,
      }

      // Добавляем в локальный список и открываем модальное окно
      setRecords([newRecord, ...records])
      setSelectedRecord(newRecord)
      setPreorderSuccess(data.message)
      setMenuSearchQuery("")
      setIsMenuOpen(false)

      console.log("[v0] Preorder created:", data)
      return newRecord
    } catch (error) {
      console.error("[v0] Error creating preorder:", error)
      // Fallback на локальное создание
      const newRecord: VinylRecord = {
        id: `preorder-${Date.now()}`,
        article_id: `PRE-${Date.now()}`,
        title: searchTerm,
        artist: "Уточняется",
        year: new Date().getFullYear(),
        country: "Уточняется",
        price: 0,
        status: "preorder" as const,
        image: "/placeholder.svg",
        genre: "Уточняется",
        label: "Уточняется",
        condition: "Новая",
        description: `Пластинка "${searchTerm}" добавлена в каталог. Мы найдём её для вас!`,
      }
      setRecords([newRecord, ...records])
      setSelectedRecord(newRecord)
      return newRecord
    } finally {
      setIsCreatingPreorder(false)
    }
  }

  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!chatInput.trim()) return

    const userMessage = chatInput.trim()
    setChatMessages((prev) => [...prev, { role: "user", content: userMessage }])
    setChatInput("")
    setIsChatTyping(true)

    await new Promise((resolve) => setTimeout(resolve, 800))

    let response = ""
    const lowerQuery = userMessage.toLowerCase()

    if (lowerQuery.includes("привет") || lowerQuery.includes("здравств")) {
      response = "Привет! 🎵 Чем могу помочь? Ищете конкретную пластинку или посоветовать что-то интересное?"
    } else if (lowerQuery.includes("достав") || lowerQuery.includes("привез") || lowerQuery.includes("когда")) {
      response = "🚚 Доставка из Москвы в Калининград раз в 2 недели. Оформите предзаказ, и мы уведомим о поступлении!"
    } else if (lowerQuery.includes("цена") || lowerQuery.includes("сколько") || lowerQuery.includes("стоимость")) {
      response = "💰 Цены от 800₽ до 5000₽ в зависимости от редкости и состояния. Найдите пластинку в поиске — там указана точная цена."
    } else if (lowerQuery.includes("jazz") || lowerQuery.includes("джаз")) {
      response = '🎷 Джаз — отличный выбор! Рекомендую Miles Davis "Kind of Blue" или John Coltrane. Введите "джаз" в поиске ↑'
      setSearchQuery("джаз")
    } else if (lowerQuery.includes("rock") || lowerQuery.includes("рок")) {
      response = '🎸 Рок: Pink Floyd, Beatles, Led Zeppelin, и многое другое! Введите "рок" в поиске или назовите исполнителя.'
      setSearchQuery("рок")
    } else if (lowerQuery.includes("совет") || lowerQuery.includes("посовету") || lowerQuery.includes("рекоменд")) {
      response = "🌟 Что предпочитаете? Рок, джаз, электронику или советские пластинки?"
    } else if (lowerQuery.includes("предзаказ") || lowerQuery.includes("заказ")) {
      response = '📦 Предзаказ бесплатный! Найдите пластинку через поиск — если нет, система предложит создать предзаказ.'
    } else if (lowerQuery.includes("спасибо") || lowerQuery.includes("благодар")) {
      response = "Пожалуйста! 🎉 Если ещё что-то нужно — пишите!"
    } else {
      // Попытка поиска
      response = `🔍 Ищу "${userMessage}"... Введите этот запрос в поисковую строку вверху страницы!`
      setSearchQuery(userMessage)
    }

    setChatMessages((prev) => [...prev, { role: "assistant", content: response }])
    setIsChatTyping(false)
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-3 sm:py-4">
          <div className="flex items-center justify-between gap-4">
            {/* Burger Menu */}
            <Sheet open={isMenuOpen} onOpenChange={setIsMenuOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="flex-shrink-0">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-80 overflow-y-auto">
                <SheetHeader className="border-b pb-4 mb-6">
                  <Link href="/" onClick={() => setIsMenuOpen(false)} className="flex flex-col items-center gap-3 hover:opacity-80 transition-opacity">
                    <div className="flex items-center gap-1">
                      <Disc3 className="h-8 w-8 text-primary" />
                      <Disc3 className="h-8 w-8 text-primary -ml-4 opacity-50" />
                    </div>
                    <div className="text-center">
                      <SheetTitle className="text-2xl font-bold text-primary">BALT-SET</SheetTitle>
                      <p className="text-xs text-muted-foreground mt-1">Виниловые пластинки в Калининграде</p>
                    </div>
                  </Link>
                </SheetHeader>

                <div className="mt-6 space-y-6">
                  {/* Search in menu */}
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      type="text"
                      placeholder="Поиск пластинки..."
                      value={menuSearchQuery}
                      onChange={(e) => setMenuSearchQuery(e.target.value)}
                      className="pl-9"
                    />
                    {menuSearchQuery && filteredRecords.length === 0 && (
                      <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <p className="text-sm text-blue-900 mb-3 font-medium">
                          Не нашли "{menuSearchQuery}"?
                        </p>
                        <p className="text-xs text-blue-700 mb-3">
                          AI автоматически создаст карточку и мы уведомим вас о поступлении!
                        </p>
                        <Button
                          size="sm"
                          className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                          onClick={() => createNewPreorder(menuSearchQuery)}
                          disabled={isCreatingPreorder}
                        >
                          {isCreatingPreorder ? "Создаём..." : "Оформить предзаказ"}
                        </Button>
                      </div>
                    )}
                  </div>

                  {/* Categories */}
                  <div className="space-y-2">
                    <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider mb-3">Жанры</h3>
                    {["Рок", "Джаз", "Классика", "Электроника", "Поп", "СССР"].map((category) => (
                      <Button
                        key={category}
                        variant="ghost"
                        className="w-full justify-start text-left hover:bg-primary/10 hover:text-primary"
                        onClick={() => {
                          setSearchQuery(category)
                          setIsMenuOpen(false)
                        }}
                      >
                        {category}
                      </Button>
                    ))}
                    <Link href="/catalog">
                      <Button
                        variant="ghost"
                        className="w-full justify-start text-left bg-primary/10 text-primary hover:bg-primary/20 hover:text-primary font-semibold"
                        onClick={() => setIsMenuOpen(false)}
                      >
                        Все категории
                      </Button>
                    </Link>
                  </div>

                  <div className="space-y-3 pt-4 border-t border-border">
                    <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider mb-3">Связь</h3>
                    <a
                      href="https://t.me/konigelectric"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-3 p-3 rounded-lg hover:bg-primary/10 transition-colors"
                    >
                      <Send className="h-5 w-5 text-[#0088cc]" />
                      <span className="text-sm font-medium">Telegram</span>
                    </a>
                    <a
                      href="https://vk.com/electro_konig"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-3 p-3 rounded-lg hover:bg-primary/10 transition-colors"
                    >
                      <svg className="h-5 w-5 text-[#0077FF]" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M15.07 2H8.93C3.33 2 2 3.33 2 8.93v6.14C2 20.67 3.33 22 8.93 22h6.14c5.6 0 6.93-1.33 6.93-6.93V8.93C22 3.33 20.67 2 15.07 2zm3.18 14.5h-1.34c-.71 0-.93-.57-2.21-1.85-1.11-1.11-1.6-1.26-1.88-1.26-.39 0-.5.11-.5.64v1.68c0 .46-.14.73-1.34.73-2.19 0-4.63-1.34-6.34-3.83C2.62 9.66 2.14 7.43 2.14 7c0-.28.11-.54.64-.54h1.34c.48 0 .66.21.85.71.93 2.58 2.49 4.84 3.13 4.84.24 0 .35-.11.35-.72V9.18c-.07-1.16-.68-1.26-.68-1.68 0-.23.18-.46.48-.46h2.11c.4 0 .55.22.55.69v3.71c0 .4.18.55.29.55.24 0 .44-.15.88-.59 1.35-1.52 2.32-3.87 2.32-3.87.13-.28.34-.54.82-.54h1.34c.57 0 .7.29.57.69-.19.96-2.23 3.88-2.23 3.88-.2.32-.27.46 0 .82.2.27.85.83 1.29 1.33.78.85 1.38 1.56 1.54 2.06.16.5-.1.76-.6.76z" />
                      </svg>
                      <span className="text-sm font-medium">ВКонтакте</span>
                    </a>
                  </div>

                  {/* Contact info */}
                  <div className="pt-4 border-t border-border space-y-2 text-sm text-muted-foreground">
                    <p className="flex items-center gap-2">
                      <span>📞</span> +7 (4012) 52-07-25
                    </p>
                    <p className="flex items-center gap-2">
                      <span>🕐</span> Пн-Сб: 10:00-19:00
                    </p>
                    <p className="flex items-center gap-2">
                      <span>📍</span> Калининград
                    </p>
                  </div>

                  <div className="pt-4">
                    <div className="relative w-full h-48 rounded-lg overflow-hidden border border-border">
                      <iframe
                        src="https://yandex.map-widget/v1/?ll=20.508,54.71&z=12&l=map"
                        width="100%"
                        height="100%"
                        frameBorder="0"
                        className="opacity-80 hover:opacity-100 transition-opacity"
                      ></iframe>
                    </div>
                  </div>
                </div>
              </SheetContent>
            </Sheet>

            <Link href="/" className="flex items-center gap-2">
              <div className="flex items-center gap-0.5">
                <Disc3 className="h-6 w-6 sm:h-7 sm:w-7 text-primary" />
                <Disc3 className="h-6 w-6 sm:h-7 sm:w-7 text-primary -ml-3 opacity-50" />
              </div>
              <span className="text-base sm:text-lg font-bold text-primary hidden sm:inline">BALT-SET</span>
            </Link>

            <div className="flex items-center gap-2 sm:gap-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDeliveriesDialog(true)}
                className="text-xs sm:text-sm hover:text-primary hidden sm:flex"
              >
                Ближайшие поставки
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowContactsDialog(true)}
                className="text-xs sm:text-sm hover:text-primary hidden sm:flex"
              >
                Контакты
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section - Clean & Minimal */}
      <section className="relative bg-gradient-to-b from-slate-50 to-white overflow-hidden">
        {/* Decorative vinyl records */}
        <div className="absolute -right-20 top-10 w-64 h-64 rounded-full border-8 border-slate-200/50 opacity-20"></div>
        <div className="absolute -left-10 bottom-0 w-48 h-48 rounded-full border-8 border-slate-200/50 opacity-20"></div>

        <div className="container mx-auto px-4 py-12 sm:py-16 md:py-20 relative z-10">
          <div className="max-w-3xl mx-auto text-center space-y-6 sm:space-y-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full text-primary text-sm font-medium">
              <Disc3 className="h-4 w-4" />
              Доставка в Калининград
            </div>
            
            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-foreground text-balance">
              Виниловые пластинки
              <span className="block text-primary">бесплатный предзаказ</span>
            </h1>
            <p className="text-base sm:text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto text-pretty">
              Найдём любую пластинку и привезём из Москвы.
            </p>

            <div className="relative max-w-xl mx-auto">
              <Search className="absolute left-5 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground z-10" />
              <Input
                type="search"
                placeholder="Название или исполнитель..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => setSearchFocused(true)}
                onBlur={() => setTimeout(() => setSearchFocused(false), 200)}
                className={`pl-14 pr-6 h-14 text-base bg-white border-2 rounded-xl shadow-lg transition-all duration-300 placeholder-muted-foreground/70 ${
                  searchFocused
                    ? "border-primary ring-4 ring-primary/10 shadow-primary/10"
                    : "border-border hover:border-primary/50"
                }`}
              />
            </div>

            {showAiAssistant && (
              <div className="mt-6 p-5 bg-white border border-border rounded-xl shadow-md animate-in slide-in-from-top-2 duration-300">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
                    <Sparkles className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1 text-left">
                    {isAiTyping ? (
                      <div className="flex gap-1.5 py-2">
                        <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce [animation-delay:0.2s]" />
                        <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce [animation-delay:0.4s]" />
                      </div>
                    ) : (
                      <p className="text-sm text-foreground leading-relaxed">{aiMessage}</p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      <main className="py-16 bg-background">
        <div className="container mx-auto px-4">
          {searchQuery && filteredRecords.length > 0 && (
            <section className="mb-16">
              <h2 className="text-3xl font-bold text-center mb-8 text-foreground">
                Результаты поиска: "{searchQuery}"
              </h2>
              <div className="space-y-3">
                {filteredRecords.map((record) => (
                  <div
                    key={record.id}
                    className="bg-white border border-border hover:border-primary/50 rounded-lg p-4 transition-all duration-200 hover:shadow-md cursor-pointer group"
                    onClick={() => {
                      setSelectedRecord(record)
                    }}
                  >
                    <div className="flex items-center gap-4">
                      <div className="relative w-16 h-16 rounded-md overflow-hidden flex-shrink-0 bg-muted">
                        <Image
                          src={record.image || "/placeholder.svg"}
                          alt={record.title}
                          fill
                          className="object-cover"
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors truncate">
                          {record.title}
                        </h3>
                        <p className="text-sm text-muted-foreground truncate">
                          {record.artist} • {record.year}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="outline" className="text-xs">
                            {record.genre}
                          </Badge>
                          <span className="text-sm font-bold text-accent">{record.price}₽</span>
                        </div>
                      </div>
                      <Button
                        size="sm"
                        className={
                          record.status === "available"
                            ? "bg-primary hover:bg-primary/90"
                            : "bg-accent hover:bg-accent/90"
                        }
                        onClick={(e) => {
                          e.preventDefault()
                          if (record.status === "available") {
                            setSelectedRecord(record)
                          } else {
                            // Logic for "Notify Me"
                          }
                        }}
                      >
                        {record.status === "available" ? "Купить" : "Уведомить"}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {searchQuery && filteredRecords.length > 0 && (
            <section className="max-w-6xl mx-auto mb-16 px-4">
              <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-6 sm:p-8 border border-border/50 shadow-sm">
                <div className="grid md:grid-cols-2 gap-8 items-center">
                  <div className="space-y-4">
                    <h3 className="text-2xl sm:text-3xl font-bold text-foreground">Мы в Калининграде</h3>
                    <div className="space-y-2 text-muted-foreground">
                      <p className="flex items-center gap-2">
                        <span className="text-primary font-semibold">📞</span> +7 (4012) 52-07-25
                      </p>
                      <p className="flex items-center gap-2">
                        <span className="text-primary font-semibold">🕐</span> Пн-Сб: 10:00-19:00
                      </p>
                      <p className="flex items-center gap-2">
                        <span className="text-primary font-semibold">📍</span> Калининград
                      </p>
                    </div>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      Прямая доставка винила из Москвы. Качество проверено, упаковка бережная. Для энтузиастов
                      качественного звука.
                    </p>
                  </div>
                  <div className="relative w-full h-64 sm:h-80 rounded-xl overflow-hidden shadow-lg border-2 border-white/50">
                    <iframe
                      src="https://yandex.map-widget/v1/?ll=20.508,54.71&z=11&l=map"
                      width="100%"
                      height="100%"
                      frameBorder="0"
                      className="grayscale-[20%] hover:grayscale-0 transition-all duration-300"
                    ></iframe>
                  </div>
                </div>
              </div>
            </section>
          )}

          {searchQuery && filteredRecords.length === 0 && (
            <div className="mt-6 text-center p-8 bg-white/80 backdrop-blur-sm rounded-2xl border-2 border-border shadow-lg">
              <p className="text-foreground font-semibold mb-2">Пластинка не найдена в каталоге</p>
              <p className="text-sm text-muted-foreground mb-5">
                AI автоматически создаст карточку предзаказа и вы сможете получить уведомление о поступлении!
              </p>
              {preorderSuccess && (
                <div className="mb-4 p-3 bg-green-100 text-green-800 rounded-lg text-sm">
                  ✅ {preorderSuccess}
                </div>
              )}
              <Button
                onClick={() => createNewPreorder(searchQuery)}
                className="bg-primary hover:bg-primary/90"
                size="lg"
                disabled={isCreatingPreorder}
              >
                {isCreatingPreorder ? "⚙️ Создаём карточку..." : "Добавить и уведомить о поступлении"}
              </Button>
            </div>
          )}

          {!searchQuery && (
            <section className="mb-16">
              <h3 className="text-2xl sm:text-3xl font-bold text-center mb-8 text-foreground">
                Популярные исполнители
              </h3>
              <div className="bg-gradient-to-br from-blue-50/50 to-purple-50/50 rounded-2xl p-6 sm:p-8 border border-border/50 shadow-sm">
                <div className="flex flex-wrap justify-center gap-2 sm:gap-3">
                  {[
                    "Pink Floyd",
                    "The Beatles",
                    "Led Zeppelin",
                    "Queen",
                    "AC/DC",
                    "Nirvana",
                    "Metallica",
                    "David Bowie",
                    "Rolling Stones",
                    "Radiohead",
                    "Deep Purple",
                    "Black Sabbath",
                    "Аквариум",
                    "Кино",
                    "ДДТ",
                    "Nautilus Pompilius",
                  ].map((tag) => (
                    <button
                      key={tag}
                      onClick={() => setSearchQuery(tag)}
                      className="text-xs sm:text-sm px-3 py-1.5 bg-white hover:bg-primary/10 border border-border hover:border-primary/50 rounded-full transition-all duration-200 hover:scale-105 hover:shadow-md text-foreground/80 hover:text-primary font-medium"
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            </section>
          )}
        </div>
      </main>

      <Dialog open={showContactsDialog} onOpenChange={setShowContactsDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-2xl">Контакты</DialogTitle>
            <DialogDescription>Свяжитесь с нами удобным способом</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="flex items-center gap-3 p-4 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors">
              <Phone className="h-5 w-5 text-primary" />
              <div>
                <p className="font-bold text-foreground text-sm">
                  <a
                    href="https://vk.com/electro_konig"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-primary transition-colors"
                  >
                    Денис Костин
                  </a>
                </p>
                <p className="text-xs text-muted-foreground">AI-ассистент музыковеда</p>
              </div>
              <div className="ml-auto flex gap-2">
                <Button variant="ghost" size="sm" className="gap-2" asChild>
                  <a href="https://vk.com/electro_konig" target="_blank" rel="noopener noreferrer">
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M15.07 2H8.93C3.33 2 2 3.33 2 8.93v6.14C2 20.67 3.33 22 8.93 22h6.14c5.6 0 6.93-1.33 6.93-6.93V8.93C22 3.33 20.67 2 15.07 2zm3.45 14.98c-.31.34-.9.45-1.53.45-1.18 0-1.86-.54-2.61-1.23-.58-.53-1.08-1-1.73-1-.71.03-1.35.6-1.83 1.14-.45.5-.84.94-1.37 1.14-.26.1-.55.15-.87.15-1.02 0-1.81-.67-2.37-1.29-.87-1-1.46-2.47-1.46-3.62 0-2.07 1.35-3.35 3.5-3.35.88 0 1.7.4 2.24 1.09.28.36.43.77.43 1.19 0 .88-.55 1.6-1.25 1.6-.41 0-.75-.33-.75-.75 0-.13.03-.26.08-.38.1-.24.11-.39.11-.47 0-.21-.17-.38-.38-.38-.47 0-.85.61-.85 1.38 0 .93.63 1.69 1.43 1.69 1.18 0 2.13-1.05 2.13-2.35 0-.67-.24-1.3-.67-1.77-.53-.59-1.28-.91-2.12-.91-1.63 0-2.75 1.04-2.75 2.6 0 .94.46 2.13 1.15 2.99.41.51.99 1 1.74 1 .21 0 .4-.03.57-.09.3-.11.58-.42.94-.84.42-.49.94-1.1 1.83-1.14 1.05-.04 1.77.6 2.47 1.23.64.58 1.3 1.18 2.26 1.18.41 0 .7-.06.88-.19.22-.15.28-.35.18-.61-.09-.23-.37-.42-.81-.42-.38 0-.69.13-.99.42-.16.15-.4.15-.56 0-.16-.16-.16-.41 0-.57.44-.42 1-.65 1.55-.65.76 0 1.38.37 1.64.98.16.38.13.8-.09 1.15z" />
                    </svg>
                    ВКонтакте
                  </a>
                </Button>

                <Button
                  onClick={() => window.open("https://t.me/konigelectric", "_blank")}
                  size="icon"
                  variant="ghost"
                  className="h-12 w-12 rounded-full hover:bg-[#0088cc]/10 flex-shrink-0"
                >
                  <Send className="h-5 w-5 text-[#0088cc]" />
                </Button>
              </div>
            </div>

            <div className="mt-4">
              <p className="text-sm text-muted-foreground mb-2">Или оставьте заявку:</p>
              <Button
                onClick={() => {
                  setShowContactsDialog(false)
                  setShowDeliveriesDialog(true)
                }}
                className="w-full bg-primary hover:bg-primary/90"
              >
                Заказать пластинку
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={showDeliveriesDialog} onOpenChange={setShowDeliveriesDialog}>
        <DialogContent className="sm:max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle className="text-2xl flex items-center gap-2">
              <Calendar className="h-6 w-6 text-primary" />
              Ближайшие поставки
            </DialogTitle>
            <DialogDescription>
              Зарезервированные пластинки в следующей поездке. Вы можете присоединиться!
            </DialogDescription>
          </DialogHeader>

          <div className="bg-gradient-to-r from-primary/10 to-accent/10 border border-primary/20 rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-foreground">Дата поездки:</span>
              <Badge className="bg-primary text-primary-foreground">25 января 2025</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="font-semibold text-foreground">Свободных мест:</span>
              <Badge variant="destructive">3 места</Badge>
            </div>
          </div>

          <p className="text-sm text-muted-foreground mb-4">
            Эти пластинки уже зарезервированы. Прямая поставка из Москвы в Калининград, можете добавить свою пластинку в
            заказ!
          </p>

          <div className="flex-1 overflow-y-auto space-y-3 pr-2">
            {reservedRecords.map((record) => (
              <div
                key={record.id}
                className="flex items-center gap-4 p-4 rounded-lg border border-border hover:border-primary/50 transition-colors cursor-pointer bg-white"
                onClick={() => {
                  setSelectedRecord(record)
                  setShowDeliveriesDialog(false)
                }}
              >
                <div className="relative w-16 h-16 rounded-md overflow-hidden flex-shrink-0 bg-muted">
                  <Image src={record.image || "/placeholder.svg"} alt={record.title} fill className="object-cover" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold text-foreground truncate">{record.title}</h4>
                  <p className="text-sm text-muted-foreground truncate">
                    {record.artist} • {record.year}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="secondary" className="text-xs">
                      {record.genre}
                    </Badge>
                    <span className="text-sm font-bold text-accent">{record.price}₽</span>
                  </div>
                </div>
                <Badge className="bg-accent/20 text-accent border-accent">Зарезервировано</Badge>
              </div>
            ))}
          </div>

          <div className="pt-4 border-t mt-4">
            <Button
              onClick={() => {
                setShowDeliveriesDialog(false)
                // setShowCustomOrderDialog(true)
              }}
              className="w-full bg-primary hover:bg-primary/90"
              size="lg"
            >
              Добавить свою пластинку
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Vinyl Modal */}
      <VinylModal record={selectedRecord} open={!!selectedRecord} onClose={() => setSelectedRecord(null)} />

      {/* Bottom Chat Bar - Clean Design */}
      <div className="fixed bottom-0 left-0 right-0 z-50 border-t border-border shadow-lg bg-white">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-3 px-4 py-3">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-sm flex-shrink-0">
              🎵
            </div>
            <div className="hidden sm:block flex-shrink-0">
              <p className="font-semibold text-sm text-foreground">
                BALT-SET
              </p>
              <p className="text-xs text-muted-foreground">AI-помощник</p>
            </div>
            <button
              onClick={() => setIsChatExpanded(!isChatExpanded)}
              className="p-2 rounded-full hover:bg-muted transition-colors sm:hidden"
            >
              {isChatExpanded ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5 text-primary"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path d="M19 13H5a1 1 0 0 0 0 2h14a1 1 0 0 0 0-2z" />
                </svg>
              ) : (
                <MessageCircle className="h-5 w-5 text-primary" />
              )}
            </button>
            <form onSubmit={handleChatSubmit} className="flex-1">
              <div className="relative">
                <Input
                  type="text"
                  placeholder="Спросите о пластинках..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  className="bg-muted/50 border-0 h-11 text-sm rounded-full shadow-sm pl-4 pr-12 focus:ring-primary/20 focus:ring-2 transition-shadow"
                />
                <Button
                  type="submit"
                  size="icon"
                  className="absolute right-1 top-1/2 -translate-y-1/2 h-9 w-9 bg-primary hover:bg-primary/90 rounded-full"
                >
                  <Send className="h-4 w-4 text-white" />
                </Button>
              </div>
            </form>
            <div className="flex gap-1">
              <Button
                onClick={() => window.open("https://t.me/konigelectric", "_blank")}
                size="icon"
                variant="ghost"
                className="h-10 w-10 rounded-full hover:bg-[#0088cc]/10 flex-shrink-0"
                title="Telegram"
              >
                <Send className="h-4 w-4 text-[#0088cc]" />
              </Button>
              <Button
                onClick={() => window.open("https://vk.com/electro_konig", "_blank")}
                size="icon"
                variant="ghost"
                className="h-10 w-10 rounded-full hover:bg-[#0077FF]/10 flex-shrink-0"
                title="VK"
              >
                <svg className="h-4 w-4 text-[#0077FF]" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M15.07 2H8.93C3.33 2 2 3.33 2 8.93v6.14C2 20.67 3.33 22 8.93 22h6.14c5.6 0 6.93-1.33 6.93-6.93V8.93C22 3.33 20.67 2 15.07 2z" />
                </svg>
              </Button>
            </div>
          </div>
        </div>

        {/* Chat expanded view */}
        {isChatExpanded && (
          <div className="bg-slate-50 border-t border-border max-w-4xl mx-auto">
            <div className="h-80 overflow-y-auto p-4 space-y-3">
              {chatMessages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div
                    className={`max-w-[80%] px-4 py-2.5 rounded-2xl ${
                      msg.role === "user"
                        ? "bg-primary text-white rounded-br-md"
                        : "bg-white text-foreground shadow-sm border border-border rounded-bl-md"
                    }`}
                  >
                    <p className="text-sm leading-relaxed">{msg.content}</p>
                  </div>
                </div>
              ))}
              {isChatTyping && (
                <div className="flex justify-start">
                  <div className="bg-white px-4 py-3 rounded-2xl rounded-bl-md shadow-sm border border-border">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce [animation-delay:0.2s]" />
                      <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce [animation-delay:0.4s]" />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
