import { defineStore } from 'pinia'

export const useCardStore = defineStore('pa', {
  state: () => ({
    selectedEnte: '',
    selectedDove: '',
    allCards: [
      {
        id: 1,
        title: 'Ministero affari esteri',
        location: 'Roma',
        keywords: ['ministero', 'esteri'],
        posizioni: 3
      },
      {
        id: 2,
        title: 'Ministero della difesa',
        location: 'Roma',
        keywords: ['ministero', 'difesa'],
        posizioni: 1
      },
      {
        id: 3,
        title: 'Agenzia delle entrate',
        location: 'Milano',
        keywords: ['agenzia', 'entrate'],
        posizioni: 2
      },
      {
        id: 4,
        title: 'Ministero dell\'istruzione',
        location: 'Roma',
        keywords: ['ministero', 'scuola'],
        posizioni: 5
      },
      {
        id: 5,
        title: 'Regione Lombardia',
        location: 'Milano',
        keywords: ['regione', 'lombardia'],
        posizioni: 1
      },
      {
        id: 6,
        title: 'Comune di Bologna',
        location: 'Bologna',
        keywords: ['comune', 'bologna'],
        posizioni: 2
      },
      {
        id: 7,
        title: 'Comune di Torino',
        location: 'Torino',
        keywords: ['comune', 'torino'],
        posizioni: 1
      },
      {
        id: 8,
        title: 'Agenzia Italia Digitale',
        location: 'Roma',
        keywords: ['agenzia', 'digitale'],
        posizioni: 4
      },
      {
        id: 9,
        title: 'Comune di Montacuto',
        location: 'Montacuto',
        keywords: ['comune', 'montacuto'],
        posizioni: 2
      }
    ]
  }),

  getters: {
    filteredCards(state) {
      console.log('🔍 Filtro cards con:', {
        ente: state.selectedEnte,
        dove: state.selectedDove
      })

      let filtered = state.allCards

      // Filtra per Ente
      if (state.selectedEnte && state.selectedEnte.trim() !== '') {
        const searchTerm = state.selectedEnte.toLowerCase().trim()
        filtered = filtered.filter(card => {
          const titleMatch = card.title.toLowerCase().includes(searchTerm)
          const keywordMatch = card.keywords.some(keyword => 
            keyword.toLowerCase().includes(searchTerm)
          )
          return titleMatch || keywordMatch
        })
        console.log(`  ✓ Filtro Ente "${searchTerm}": ${filtered.length} risultati`)
      }

      // Filtra per Dove
      if (state.selectedDove && state.selectedDove.trim() !== '') {
        const searchLocation = state.selectedDove.toLowerCase().trim()
        filtered = filtered.filter(card => 
          card.location.toLowerCase().trim() === searchLocation
        )
        console.log(`  ✓ Filtro Dove "${searchLocation}": ${filtered.length} risultati`)
      }

      console.log(`  📊 Totale risultati: ${filtered.length}`)
      return filtered
    },

    enteOptions(state) {
      const keywords = new Set()
      state.allCards.forEach(card => {
        keywords.add(card.title)
        card.keywords.forEach(keyword => keywords.add(keyword))
      })
      const options = Array.from(keywords).sort()
      console.log('📋 Opzioni Ente generate:', options.length)
      return options
    },

    doveOptions(state) {
      const locations = new Set(state.allCards.map(card => card.location))
      const options = Array.from(locations).sort()
      console.log('📋 Opzioni Dove generate:', options.length)
      return options
    }
  },

  actions: {
    setSelectedEnte(value) {
      console.log('🏛️ setSelectedEnte chiamato:', value)
      this.selectedEnte = value || ''
    },

    setSelectedDove(value) {
      console.log('📍 setSelectedDove chiamato:', value)
      this.selectedDove = value || ''
    },

    resetFilters() {
      console.log('🔄 Reset filtri')
      this.selectedEnte = ''
      this.selectedDove = ''
    }
  }
})