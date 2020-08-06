/* jshint esversion: 6 */

// the query parameters in the vuejs app
// and their mapping to the query string
// of teh web page or the ajax request
// [VUE_DATA_NAME, QUERY_STRING_NAME, TYPE, DEFAULT_VALUE]
const VUE_QS_MAPPING = [
  ['group', 'group', 'lowercase', 'declaration'],
  ['parent', 'parent', 'lowercase', 'v1'],
]

const PRESELECTED_TEXT_SIGLA = ['V1']

const API_PATH_TEXTS_LIST = '/api/texts/?'
const GROUP_DEFAULT = 'declaration';

// which texts are displayed by default in the Viewer for Regiam and Declaration
const DEFAULT_SIGLUMS = {'declaration': 'O', 'regiam': 'C'}

// Content loading statuses
const STATUS_INITIAL = 0
const STATUS_TO_FETCH = 1
const STATUS_FETCHING = 2
const STATUS_FETCHED = 3
const STATUS_ERROR = 4

const COLOR_BASE_INTENSITY = 200
// const COLOR_GROUP_FIRST = [200, 255, 200]
const COLOR_GROUP_FIRST = [225, 255, 225]
const COLOR_GROUP_LAST = [COLOR_BASE_INTENSITY,COLOR_BASE_INTENSITY, 255]
const COLOR_MOST_DISTANT = [255, 80, 80]

// are the w-regions highlighted by default
const DISPLAY_WREGIONS_DEFAULT = true

const Vue = window.Vue

const HIGHLIGHT_CLASS = 'highlighted'

// types of views
const TYPES_LABEL = {
  transcription: 'Latin',
  translation: 'English translation',
  histogram: 'Bar chart'
}

const HISTOGRAM_VIEW = 'histogram'
const WINDOW_INNER_WIDTH = window.innerWidth

const FULLSCREEN_BLOCK = 'show-fullscreen'

function clog(...messages) {
  window.console.log(...messages)
}

function blend_colors(c1, c2, ratio) {
    // c1, c2: two colors, each one is an RGB array
    // return a new rgb array that blends c1 with c2
    // with ratio (between 0 and 1).
    // 0: closer to c1, 1: closer the c2
    if (isNaN(ratio)) return c1;

    let ret = []
    for (let i=0; i<3; i++) {
       ret.push(c1[i] + ratio * (c2[i] - c1[i]))
    }
    return ret
}


$(() => {
  let app = new Vue({
    el: '#lab-regions',
    data: {
      status: STATUS_FETCHED,
      group: 'declaration',
      parent: 'custom',

      panels: {
        'table': 'Table',
        'settings': 'Settings',
        'help': 'Help',
      },
      panel: 'settings',
      /*
      List of all available texts. Exactly as returned by /api/texts/.

      texts: [{
        id: <TEXT_ID>,
        type: 'manuscript'|'version'|'work',
        list_heading: 'manuscript'|'version'|'work',
        attributes: {
          siglum: ,
          name: ,
          group: <ID_OF_A_TEXT>,
        }
      }, [...]]
      */
      is_reading_distant: 0,

      texts: [],
      regions: [
      ],
      regions_meta: {},
    },
    mounted() {
      let self = this

      this._set_vue_from_query_string();

      $.getJSON(API_PATH_TEXTS_LIST+'&group='+self.group).done((res) => {
        Vue.set(self, 'texts', res.data)

        // add direct references to parent texts
        // for convenience in the template.
        for (let text of this.texts) {
          text.parent = this.get_text_from_id_or_siglum(text.attributes.group)
        }

        // select the texts from the query string
        const params = new URLSearchParams(window.location.search);
        let qs_text_ids = params.get('texts')
        if (qs_text_ids) {
            qs_text_ids = qs_text_ids.split(',')
        } else {
            qs_text_ids = PRESELECTED_TEXT_SIGLA
        }

        for (let siglum of qs_text_ids) {
          let text = self.get_text_from_id_or_siglum(siglum)
          if (text) {
              text.selected = true
          }
        }

        this.fetch_regions()
      })

    },
    computed: {
      view_types: function () {
        return TYPES_LABEL
      },
      text_types: function () {
        return [
          { label: 'Work', type: 'work' },
          { label: 'Versions', type: 'version' },
          { label: 'Manuscripts', type: 'manuscript' }
        ]
      }
    },
    watch: {
      parent: function() {
        this.fetch_regions()
      },
    },
    filters: {
      lowercase: function(value) {
        return value.toLowerCase()
      },
      view_type_label: function (value) {
        return TYPES_LABEL[value]
      }
    },
    methods: {
      on_tick_text: function (text, silent) {
        // TODO: deduplicate from text_search.js
        let selected = text.selected

        if (text.type == 'version') {
          // select all members accordingly
          for (let member of this.texts) {
            if (member.parent === text) {
              member.selected = selected
            }
          }
        }
        if (text.type == 'manuscript') {
          // deselect parent of member if unselected
          if (!selected) {
            text.parent.selected = selected
          }
        }

        if (!silent) this.fetch_regions()
      },
      get_reading_style: function(reading, region) {
        if (region.groups == 1) return ''

        let color = blend_colors(
          COLOR_GROUP_FIRST,
          COLOR_GROUP_LAST,
          reading.grp / (region.groups - 1)
        )
        color = blend_colors(color, COLOR_MOST_DISTANT, reading.dist * 0.8)
        return 'background-color: rgb(' + color.join(',') + ')'
      },
      fetch_regions: function() {
        if (this.status != STATUS_FETCHED) {
            return
        }

        this.status = STATUS_FETCHING

        let self = this

        // array of of selected text ids
        let text_ids = this.texts.map(function(t) {
          if (t.selected) return t.id
        }).filter(aid => aid)

        $.getJSON(
            '/lab/api/regions/compare/',
            {
                group: self.group,
                parent: self.parent,
                texts: text_ids.join(','),
            }
        ).done((res) => {
            Vue.set(self, 'regions', res.data)
            Vue.set(self, 'regions_meta', res.meta)
            self.update_query_string()
            self.status = STATUS_FETCHED
        })
      },
      update_query_string: function () {
        // update query string with current state of viewer
        // e.g. ?blocks=506:transcription,transcription;495:transcription
        var self = this
        let qs = 'group=' + self.group + '&parent=' + self.parent

        let text_ids = this.texts.map(function(t) {
          if (t.selected) return t.id
        }).filter(aid => aid).join(',')
        qs += '&texts='+text_ids

        qs = window.location.href.replace(
          /^([^?]+)([^#]+)(.*)$/,
          '$1?' + qs + '$3'
        )

        if (qs != window.location.href) {
            history.pushState(null, '', qs)
        }
      },

      _set_vue_from_query_string: function() {
        // initialise facet selection from the query string
        // Except the texts (see mounted)
        const params = new URLSearchParams(window.location.search);
        for (const m of VUE_QS_MAPPING) {
          let val = params.get(m[1])
          val = (val === undefined || val === null) ? m[3] : val;
          if (m[2] === 'int') {
            val = parseInt(val)
            if (isNaN(val)) val = m[3]
          }
          if (m[2] === 'lowercase') {
            val = val.toLowerCase()
          }
          this[m[0]] = val
        }
      },

      get_text_from_id_or_siglum: function (id_or_siglum) {
        // Gotcha: some texts share the same siglum, e.g. PA in v5 and v6!
        //
        id_or_siglum += ''
        for (let text of this.texts) {
          if (
            text.id == id_or_siglum ||
            text.attributes.siglum.toLowerCase() == id_or_siglum.toLowerCase()
          ) {
            return text
          }
        }
        return null
      },

    }
  })
})
