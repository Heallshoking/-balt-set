"use client"

import { useState, useEffect, useMemo } from "react"
import { Search, Disc3, Menu, Sparkles, TrendingUp, Clock, Users } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { VinylCard } from "@/components/vinyl-card"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"

const API_URL = "http://176.98.178.109:8000/api/records"
const PREORDER_API = "http://176.98.178.109:8000/api/preorder"

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
  stock?: number // ← новый флаг для дефицита
}

export default function HomePage() {
  const [records, setRecords] = useState<VinylRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isCreatingPreorder, setIsCreatingPreorder] = useState(false)

  // === Фильтрация с мемоизацией ===
  const filteredRecords = useMemo(() => {
    if (!searchQuery.trim()) return records
    const q = searchQuery.toLowerCase()
    return records.filter(
      (r) =>
        r.title.toLowerCase().includes(q) ||
        r.artist.toLowerCase().includes(q) ||
        r.genre?.toLowerCase().includes(q)
    )
  }, [records, searchQuery])

  // === Топ предзаказов (социальное доказательство) ===
  const popularPreorders = useMemo(() => {
    return records
      .filter((r) => r.status === "preorder" && (r.preorder_count || 0) > 0)
      .sort((a, b) => (b.preorder_count || 0) - (a.preorder_count || 0))
      .slice(0, 10)
  }, [records])

  // === Загрузка данных ===
  useEffect(() => {
    async function fetchRecords() {
      try {
        const response = await fetch(API_URL, {
          method: "GET",
          headers: { Accept: "application/json" },
        })

        if (!response.ok) throw new Error(`HTTP ${response.status}`)

        const data = await response.json()

        if (data?.records && Array.isArray(data.records)) {
          const formatted = data.records.map((r: any): VinylRecord => {
            // ← Приведение статуса к унифицированному виду
            let status: VinylRecord["status"] = "available"
            if (r.status?.includes("Предзаказ")) status = "preorder"
            else if (r.status?.includes("Продана")) status = "sold"
            else if (r.status?.includes("Доступна")) status = "available"

            return {
              id: r.article_id || r.id || String(Date.now() + Math.random()),
              article_id: r.article_id,
              title: r.title || "Без названия",
              artist: r.artist || "Неизвестный исполнитель",
              year: Number(r.year) || 0,
              country: r.country || "Россия",
              price: Number(r.price) || 0,
              status,
              image: r.photo_url || r.image || "/placeholder.svg",
              photo_url: r.photo_url,
              genre: r.genre,
              label: r.label,
              condition: r.condition,
              description: r.description,
              preorder_count: r.preorder_count != null ? Number(r.preorder_count) : 0, // ← реальные данные!
              stock: r.stock != null ? Number(r.stock) : undefined,
            }
          })

          setRecords(formatted)
        }
      } catch (error) {
        console.error("Ошибка загрузки записей:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchRecords()
  }, [])

  // === Создание предзаказа (взаимность + облегчённый CTA) ===
  const handleCreatePreorder = async () => {
    if (!searchQuery.trim() || isCreatingPreorder) return

    setIsCreatingPreorder(true)
    try {
      const response = await fetch(PREORDER_API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ search_query: searchQuery.trim() }),
      })

      if (response.ok) {
        alert("✅ Отлично! Вы первым узнаете о поступлении этой пластинки — бесплатно.")
        setSearchQuery("")
      } else {
        alert("⚠️ Не удалось создать предзаказ. Попробуйте позже.")
      }
    } catch (error) {
      console.error("Ошибка предзаказа:", error)
      alert("⚠️ Произошла ошибка. Проверьте соединение.")
    } finally {
      setIsCreatingPreorder(false)
    }
  }

  // === Доступные пластинки ===
  const availableRecords = records.filter((r) => r.status === "available")

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-white/90 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 sm:px-6 py-3">
          <div className="flex items-center justify-between gap-4">
            <Sheet open={isMenuOpen} onOpenChange={setIsMenuOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-80 sm:w-96 overflow-y-auto px-6">
                <SheetHeader className="border-b pb-4 mb-6">
                  <Link href="/" onClick={() => setIsMenuOpen(false)} className="flex flex-col items-center gap-3">
                    <div className="flex items-center gap-1">
                      <Disc3 className="h-8 w-8 text-primary" />
                      <Disc3 className="h-8 w-8 text-primary -ml-4 opacity-50" />
                    </div>
                    <div className="text-center">
                      <SheetTitle className="text-2xl font-bold text-primary">BALT-SET</SheetTitle>
                      <p className="text-xs text-muted-foreground mt-1">Винил в Калининграде с 2010 г.</p>
                    </div>
                  </Link>
                </SheetHeader>

                <div className="space-y-6">
                  <div className="space-y-2">
                    <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider mb-2">Жанры</h3>
                    {["Рок", "Джаз", "Классика", "Электроника", "Поп", "СССР"].map((genre) => (
                      <Button
                        key={genre}
                        variant="ghost"
                        className="w-full justify-start text-left hover:bg-primary/10"
                        onClick={() => {
                          setSearchQuery(genre)
                          setIsMenuOpen(false)
                        }}
                      >
                        {genre}
                      </Button>
                    ))}
                    <Link href="/catalog" onClick={() => setIsMenuOpen(false)}>
                      <Button variant="ghost" className="w-full justify-start text-left bg-primary/10 text-primary">
                        Все жанры
                      </Button>
                    </Link>
                  </div>

                  <div className="pt-4 border-t border-border text-sm text-muted-foreground">
                    <p className="flex items-center gap-2">📞 +7 (4012) 52-07-25</p>
                    <p className="flex items-center gap-2">🕐 Пн–Сб: 10:00–19:00</p>
                    <p className="flex items-center gap-2">📍 Калининград, ул. Дм. Донского, 7</p>
                  </div>
                </div>
              </SheetContent>
            </Sheet>

            <Link href="/" className="flex items-center gap-2">
              <Disc3 className="h-6 w-6 text-primary" />
              <Disc3 className="h-6 w-6 text-primary -ml-3 opacity-50" />
              <span className="font-bold text-primary hidden sm:inline">BALT-SET</span>
            </Link>

            <Button variant="ghost" size="sm" className="hidden sm:flex" asChild>
              <Link href="/contacts">Контакты</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero: Взаимность + Авторитет */}
      <section className="relative bg-gradient-to-b from-slate-50 to-white py-12 sm:py-16">
        <div className="container mx-auto px-4 text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full text-primary text-sm font-medium">
            <Disc3 className="h-4 w-4" /> Бесплатный предзаказ — без предоплаты!
          </div>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground">
            Виниловые пластинки<br />
            <span className="text-primary">с бесплатным предзаказом</span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Найдём и привезём любую пластинку из Москвы. Уведомим первым — без SMS-спама.
          </p>

          <div className="relative max-w-xl mx-auto">
            <Search className="absolute left-5 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Название, артист или жанр..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleCreatePreorder()}
              className="pl-14 pr-6 h-14 text-base bg-white border-2 rounded-xl shadow-lg"
            />
          </div>
        </div>
      </section>

      {/* Популярные предзаказы — социальное доказательство */}
      {popularPreorders.length > 0 && (
        <section className="py-8 bg-gradient-to-r from-primary/5 to-purple-500/5">
          <div className="container mx-auto px-4">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">🔥 Популярные предзаказы</h2>
                <p className="text-sm text-muted-foreground">Самые ожидаемые пластинки этой недели</p>
              </div>
            </div>
            <div className="overflow-x-auto pb-4">
              <div className="flex gap-4 w-max">
                {popularPreorders.map((record) => (
                  <div key={record.id} className="w-48 flex-shrink-0">
                    <VinylCard record={record} compact />
                    <div className="mt-2 flex items-center gap-1 text-xs text-muted-foreground">
                      <Users className="h-3 w-3" />
                      <span>{record.preorder_count} коллекционеров ждут</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Популярные артисты — симпатия + привычка */}
      <section className="py-8">
        <div className="container mx-auto px-4">
          <h2 className="text-2xl font-bold mb-6">Любимые исполнители наших покупателей</h2>
          <div className="flex flex-wrap gap-2">
            {["Pink Floyd", "The Beatles", "Miles Davis", "Led Zeppelin", "Queen", "Кино", "Аквариум", "Nirvana"].map((artist) => (
              <Badge
                key={artist}
                variant="secondary"
                className="cursor-pointer hover:bg-primary hover:text-primary-foreground px-4 py-2 text-sm transition-colors"
                onClick={() => setSearchQuery(artist)}
              >
                {artist}
              </Badge>
            ))}
          </div>
        </div>
      </section>

      {/* В наличии — дефицит + авторитет */}
      <section className="py-8 bg-gradient-to-br from-slate-50 to-white border-y border-border">
        <div className="container mx-auto px-4">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
              <Disc3 className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">В наличии — можно купить сегодня</h2>
              <p className="text-sm text-muted-foreground">Ограниченное количество. Обновляется ежедневно.</p>
            </div>
          </div>

          {availableRecords.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {availableRecords.slice(0, 10).map((record) => (
                <VinylCard key={record.id} record={record} compact />
              ))}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">Сейчас нет пластинок в наличии. Следите за обновлениями!</p>
          )}
        </div>
      </section>

      {/* Результаты поиска / предзаказ — обязательство + взаимность */}
      <section className="pb-16">
        <div className="container mx-auto px-4">
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
              <p className="mt-4 text-muted-foreground">Загружаем редкие винилы из архива...</p>
            </div>
          ) : searchQuery ? (
            <div>
              {filteredRecords.length > 0 ? (
                <div className="bg-white rounded-2xl p-6 shadow-sm border border-border mb-6">
                  <p className="text-lg font-semibold mb-4">
                    Найдено {filteredRecords.length}{" "}
                    {(() => {
                      const n = filteredRecords.length
                      if (n % 10 === 1 && n % 100 !== 11) return "пластинка"
                      if (n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20)) return "пластинки"
                      return "пластинок"
                    })()} по запросу «{searchQuery}»
                  </p>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                    {filteredRecords.map((record) => (
                      <VinylCard key={record.id} record={record} compact />
                    ))}
                  </div>

                  {/* CTA: создать предзаказ — даже если что-то нашлось */}
                  <div className="mt-8 p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
                    <div className="flex items-start gap-4">
                      <Clock className="h-6 w-6 text-blue-600 mt-0.5" />
                      <div>
                        <h3 className="font-bold text-blue-900">Не то, что искали?</h3>
                        <p className="text-sm text-blue-700 mb-3">
                          Мы бесплатно добавим ваш запрос в список поставок и уведомим первым.
                        </p>
                        <Button
                          onClick={handleCreatePreorder}
                          disabled={isCreatingPreorder}
                          className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white"
                        >
                          {isCreatingPreorder ? "Добавляем..." : "Добавить в список поставок"}
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-2xl p-8 shadow-sm border border-border text-center max-w-2xl mx-auto">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center mx-auto mb-4">
                    <Sparkles className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="text-xl font-bold mb-2">Такой пластинки пока нет</h3>
                  <p className="text-muted-foreground mb-6">
                    Но вы можете первым узнать о её поступлении — бесплатно и без спама.
                  </p>
                  <Button
                    onClick={handleCreatePreorder}
                    disabled={isCreatingPreorder}
                    size="lg"
                    className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white"
                  >
                    {isCreatingPreorder ? "Добавляем..." : "Уведомить о поступлении"}
                  </Button>
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