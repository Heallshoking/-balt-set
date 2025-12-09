"use client"

import { useState, useEffect } from "react"
import { Search, Disc3, Menu, Sparkles, TrendingUp } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { VinylCard } from "@/components/vinyl-card"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"

const API_URL = "http://176.98.178.109:8000/api/records"

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
  preorder_count?: number
}

export default function HomePage() {
  const [records, setRecords] = useState<VinylRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isCreatingPreorder, setIsCreatingPreorder] = useState(false)

  const filteredRecords = searchQuery
    ? records.filter(
        (r: VinylRecord) =>
          r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          r.artist.toLowerCase().includes(searchQuery.toLowerCase()) ||
          r.genre?.toLowerCase().includes(searchQuery.toLowerCase()),
      )
    : records

  // Популярные пластинки с наибольшим количеством предзаказов
  const popularPreorders = records
    .filter((r: VinylRecord) => r.status === "preorder" && (r.preorder_count || 0) > 0)
    .sort((a: VinylRecord, b: VinylRecord) => (b.preorder_count || 0) - (a.preorder_count || 0))
    .slice(0, 10)

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
          const formattedRecords = data.records.map((r: any) => ({
            id: r.article_id || r.id || String(Math.random()),
            article_id: r.article_id,
            title: r.title,
            artist: r.artist,
            year: r.year,
            country: r.country || "Россия",
            price: r.price,
            status:
              r.status === "🟢 Доступна" || r.status === "available"
                ? "available"
                : r.status === "🟡 Предзаказ" || r.status === "preorder"
                  ? "preorder"
                  : r.status === "🔴 Продана" || r.status === "sold"
                    ? "sold"
                    : "available",
            image: r.photo_url || r.image || "/placeholder.svg",
            photo_url: r.photo_url,
            genre: r.genre,
            label: r.label,
            condition: r.condition,
            description: r.description,
            preorder_count: Math.floor(Math.random() * 20), // TODO: получать из API
          }))

          setRecords(formattedRecords)
        }
        setLoading(false)
      } catch (error) {
        console.error("Ошибка загрузки:", error)
        setLoading(false)
      }
    }

    fetchRecords()
    
    // Auto-refresh every 2 minutes to ensure data is up to date
    const interval = setInterval(fetchRecords, 120000)
    return () => clearInterval(interval)
  }, [])

  const createNewPreorder = async (query: string) => {
    setIsCreatingPreorder(true)
    try {
      const response = await fetch("http://176.98.178.109:8000/api/preorder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ search_query: query }),
      })

      if (response.ok) {
        alert("✅ Предзаказ создан! Мы уведомим вас о поступлении.")
      }
    } catch (error) {
      console.error("Ошибка создания предзаказа:", error)
    } finally {
      setIsCreatingPreorder(false)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 sm:px-6 py-3 sm:py-4">
          <div className="flex items-center justify-between gap-4">
            {/* Burger Menu */}
            <Sheet open={isMenuOpen} onOpenChange={setIsMenuOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="flex-shrink-0">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-80 sm:w-96 overflow-y-auto px-6">
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

                <div className="space-y-6">
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
                className="text-xs sm:text-sm hover:text-primary hidden sm:flex"
              >
                Контакты
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative bg-gradient-to-b from-slate-50 to-white overflow-hidden">
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
                className="pl-14 pr-6 h-14 text-base bg-white border-2 rounded-xl shadow-lg"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Popular Preorders Slider */}
      {popularPreorders.length > 0 && (
        <section className="py-8 bg-gradient-to-r from-primary/5 via-purple-500/5 to-primary/5">
          <div className="container mx-auto px-4">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-foreground">Популярные предзаказы</h2>
                <p className="text-sm text-muted-foreground">Пластинки с наибольшим интересом</p>
              </div>
            </div>
            
            <div className="overflow-x-auto pb-4">
              <div className="flex gap-4 w-max">
                {popularPreorders.map((record) => (
                  <div key={record.id} className="w-48 flex-shrink-0">
                    <VinylCard record={record} compact />
                    <div className="mt-2 flex items-center gap-1 text-xs text-muted-foreground">
                      <Sparkles className="h-3 w-3" />
                      <span>{record.preorder_count} чел. интересуются</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Popular Artists Tags */}
      <section className="py-8">
        <div className="container mx-auto px-4">
          <h2 className="text-2xl font-bold text-foreground mb-6">Популярные исполнители</h2>
          <div className="flex flex-wrap gap-2">
            {["Pink Floyd", "The Beatles", "Miles Davis", "Led Zeppelin", "Queen", "Deep Purple", "Кино", "Аквариум", "Metallica", "Nirvana"].map((artist) => (
              <Badge
                key={artist}
                variant="outline"
                className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors px-4 py-2 text-sm"
                onClick={() => setSearchQuery(artist)}
              >
                {artist}
              </Badge>
            ))}
          </div>
        </div>
      </section>

      {/* Available Vinyl Records Showcase */}
      <section className="py-8 bg-gradient-to-br from-slate-50 to-white border-y border-border">
        <div className="container mx-auto px-4">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
              <Disc3 className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-foreground">Пластинки в наличии</h2>
              <p className="text-sm text-muted-foreground">Готовы к покупке и доставке</p>
            </div>
          </div>
          
          {records.filter((r: VinylRecord) => r.status === "available").length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {records
                .filter((r: VinylRecord) => r.status === "available")
                .slice(0, 10)
                .map((record: VinylRecord) => (
                  <VinylCard key={record.id} record={record} compact />
                ))}
            </div>
          ) : (
            <div className="bg-white rounded-xl p-6 shadow-sm border border-border text-center">
              <p className="text-muted-foreground">На данный момент нет доступных пластинок</p>
            </div>
          )}
        </div>
      </section>

      {/* Search Results */}
      <section className="pb-16">
        <div className="container mx-auto px-4">
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
              <p className="mt-4 text-muted-foreground">Загрузка каталога...</p>
            </div>
          ) : searchQuery ? (
            <div>
              {filteredRecords.length > 0 ? (
                <div className="bg-white rounded-2xl p-6 shadow-sm border border-border mb-6">
                  <p className="text-lg font-semibold text-foreground mb-4">
                    Найдено {filteredRecords.length} {filteredRecords.length === 1 ? 'пластинка' : filteredRecords.length < 5 ? 'пластинки' : 'пластинок'} по запросу "{searchQuery}"
                  </p>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                    {filteredRecords.map((record) => (
                      <VinylCard key={record.id} record={record} compact />
                    ))}
                  </div>
                  
                  {/* Not Found Notice inside results */}
                  <div className="mt-8 p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-200 shadow-sm">
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
                        <Sparkles className="h-6 w-6 text-white" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-blue-900 mb-2">Не нашли нужную пластинку?</h3>
                        <p className="text-sm text-blue-700 mb-4">
                          AI автоматически создаст карточку предзаказа, и мы уведомим вас о поступлении!
                        </p>
                        <Button
                          onClick={() => createNewPreorder(searchQuery)}
                          className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-md"
                          disabled={isCreatingPreorder}
                        >
                          {isCreatingPreorder ? "⚙️ Создаём..." : "✨ Создать предзаказ"}
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-2xl p-8 shadow-sm border border-border text-center">
                  <div className="max-w-md mx-auto">
                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center mx-auto mb-4">
                      <Sparkles className="h-8 w-8 text-white" />
                    </div>
                    <h3 className="text-xl font-bold text-foreground mb-2">Пластинка не найдена в каталоге</h3>
                    <p className="text-sm text-muted-foreground mb-6">
                      AI автоматически создаст карточку предзаказа и вы сможете получить уведомление о поступлении!
                    </p>
                    <Button
                      onClick={() => createNewPreorder(searchQuery)}
                      className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg"
                      size="lg"
                      disabled={isCreatingPreorder}
                    >
                      {isCreatingPreorder ? "⚙️ Создаём карточку..." : "✨ Добавить и уведомить о поступлении"}
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {records.slice(0, 20).map((record) => (
                <VinylCard key={record.id} record={record} compact />
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
