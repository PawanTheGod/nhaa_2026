import React, { useState, useEffect } from 'react';
import { ASSETS } from '../assets';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const slides = [
  { id: 1, img: ASSETS.banner1 },
  { id: 2, img: ASSETS.banner2 },
  { id: 3, img: ASSETS.banner3 },
  { id: 4, img: ASSETS.banner4 },
  { id: 5, img: ASSETS.banner5 },
];

const HeroSection = () => {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setCurrent(p => (p + 1) % slides.length), 5000);
    return () => clearInterval(t);
  }, []);

  const goPrev = () => setCurrent(p => (p - 1 + slides.length) % slides.length);
  const goNext = () => setCurrent(p => (p + 1) % slides.length);

  return (
    <section className="relative w-full overflow-hidden bg-[#001f5b]" style={{ minHeight: '420px' }}>
      {/* Slides */}
      {slides.map((slide, i) => (
        <div
          key={slide.id}
          className={`absolute inset-0 transition-opacity duration-700 ${i === current ? 'opacity-100 z-10' : 'opacity-0 z-0'}`}
        >
          <img
            src={slide.img}
            alt={`Banner ${i + 1}`}
            className="w-full h-full object-cover object-center"
            style={{ minHeight: '420px' }}
            onError={e => { e.target.parentElement.style.display = 'none'; }}
          />
          {/* Overlay gradient for text readability */}
          <div className="absolute inset-0 bg-gradient-to-r from-[#001f5b]/60 via-transparent to-transparent"></div>
        </div>
      ))}

      {/* Samavesh Desktop Banner overlay */}
      <div className="absolute inset-0 z-0 pointer-events-none opacity-0">
        <img src={ASSETS.samaveshDesktopBanner} alt="" className="w-full h-full object-cover" />
      </div>

      {/* Prev/Next */}
      <button
        onClick={goPrev}
        className="absolute left-3 top-1/2 -translate-y-1/2 z-20 w-10 h-10 rounded-full bg-black/30 hover:bg-black/50 text-white flex items-center justify-center transition-all"
        aria-label="Previous"
      >
        <ChevronLeft size={20} />
      </button>
      <button
        onClick={goNext}
        className="absolute right-3 top-1/2 -translate-y-1/2 z-20 w-10 h-10 rounded-full bg-black/30 hover:bg-black/50 text-white flex items-center justify-center transition-all"
        aria-label="Next"
      >
        <ChevronRight size={20} />
      </button>

      {/* Dots */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20 flex gap-2">
        {slides.map((_, i) => (
          <button
            key={i}
            onClick={() => setCurrent(i)}
            className={`rounded-full transition-all duration-300 ${i === current ? 'w-7 h-2.5 bg-[#FF6200]' : 'w-2.5 h-2.5 bg-white/50 hover:bg-white/80'}`}
            aria-label={`Slide ${i + 1}`}
          />
        ))}
      </div>
    </section>
  );
};

export default HeroSection;
