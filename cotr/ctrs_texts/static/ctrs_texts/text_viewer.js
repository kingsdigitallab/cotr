/* jshint esversion: 6 */

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

// are the w-regions highlighted by default
const DISPLAY_WREGIONS_DEFAULT = true

const Vue = window.Vue

const HIGHLIGHT_CLASS = 'highlighted'

// types of views
const TEXT_TYPES_LABEL = window.CDS.TEXT_TYPES_LABEL;

const HISTOGRAM_VIEW = 'histogram'
const WINDOW_INNER_WIDTH = window.innerWidth

const FULLSCREEN_BLOCK = 'show-fullscreen'

function clog(...messages) {
  window.console.log(...messages)
}

$(() => {
  let app = new Vue({
    el: '#text-viewer',
    data: {
      group: 'declaration',
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
      texts: [],
      /*
      List of all UI Blocks and their Views.
      A block is a UI unit for a particular text.
      A view is a UI unit for a view of that text.

      blocks: [{
        text: <REFERENCE TO this.texts[i]>,
        comparative: <BOOLEAN>,
        views: [
          status: STATUS_XXX,
          type: 'transcription'|'translation'|'histogram'|...
          chunk: <HTML content for this view type of the text>
        ]
      }, [...]
      ]
      */
      blocks: [],
      // an id counter for block so we can locate then with jquery
      last_block_id: 0
    },
    mounted() {
      let self = this

      self.group = this._get_group_from_query_string();

      $.getJSON(API_PATH_TEXTS_LIST+'&group='+self.group).done((res) => {
        Vue.set(self, 'texts', res.data)

        // add direct references to parent texts
        // for convenience in the template.
        for (let text of this.texts) {
          text.parent = this.get_text_from_id_or_siglum(text.attributes.group)
        }

        self.init_blocks()
      })
    },
    computed: {
      view_types: function () {
        return TEXT_TYPES_LABEL
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
      blocks: {
        handler: function () {
          // Something has changed in a block or view,
          // fetch view content if needed.
          let qs = ''
          for (let block of this.blocks) {
            for (let view of block.views) {
              if (view.status === STATUS_TO_FETCH) {
                this.on_view_changed(block, view)
              }
            }
          }
          this.update_query_string()
        },
        deep: true
      }
    },
    filters: {
      view_type_label: function (value) {
        return TEXT_TYPES_LABEL[value]
      }
    },
    methods: {
      change_view_type: function (block, view, view_type) {
        view.type = view_type
        this.on_view_changed(block, view)
      },

      toggle_fullscreen(block) {
        // toggle fullscreen for this block

        block_id = '#block-' + block.id
        canvas_id = "#wrapper-" + block.id

        // Make the off-canvas-wrapper fixed as well
        const off_canvas = document.querySelector(canvas_id)
        off_canvas.classList.toggle('off-canvas-fixed')

        const name_class = document.querySelector(block_id)
        name_class.classList.toggle('fullscreen-view')
      },

      toggle_view_display(block, view, display_type) {
        // toggle a display setting for this view
        // all display setttings are prefixed with display_
        let display_key = 'display_' + display_type
        let v = view[display_key]
        Vue.set(view, display_key, !v)
      },

      on_view_changed: function (block, view) {
        // a view needs its content to be fetched
        view.status = STATUS_FETCHING
        let self = this
        $.getJSON(
          '/api/texts/' + block.text.id + '/' + view.type + '/whole/whole/'
        )
          .done((res) => {
            for (const k of Object.keys(res.data.attributes)) {
              Vue.set(view, k, res.data.attributes[k])
            }
            // view.chunk = res.data.attributes.chunk;
            view.status = STATUS_FETCHED

            // add javascript interactions to the text chunk
            Vue.nextTick(function () {
              self._after_chunk_loaded(block, view)
            })
          })
          .fail((res) => {
            view.status = STATUS_ERROR
          })
      },

      on_change_text: function (block, text, region_id) {
        // change the text of a block
        // according to the user selection in the UI
        block.sublocation = region_id
        if (text === null || block.text == text) {
          // text already loaded in that block
          // we just scroll to region_id
          this.scroll_to_sublocation(block)
        } else {
          block.text = text
          for (let view of block.views) {
            // this will trigger a request for content
            view.status = STATUS_TO_FETCH
          }
        }
      },

      scroll_to_sublocation: function (block) {
        let $block = this._get_block_div(block)
        $block.find('.' + HIGHLIGHT_CLASS).removeClass(HIGHLIGHT_CLASS)
        $block.find('.card-section').each(function (vi, view) {
          let $view = $(view)
          let $subl = $view.find('[data-rid="' + block.sublocation + '"]')
          if ($subl.length < 1) return
          $subl.addClass(HIGHLIGHT_CLASS)
          $view.scrollTop(
            $view.scrollTop() +
              $subl.position().top -
              $view.height() / 2 +
              $subl.height() / 2
          )
        })
      },

      update_query_string: function () {
        // update query string with current state of viewer
        // e.g. ?blocks=506:transcription,transcription;495:transcription
        var self = this
        let qs =
          'group=' + self.group +
          '&blocks=' +
          self.blocks
            .map(function (b) {
              let ret = ''
              if (b.text) {
                ret = b.text.id + ':' + b.views.map((v) => v.type).join(',')
                if (b.sublocation) {
                  ret += '@' + b.sublocation
                }
              }
              return ret
            })
            .join(';')
        qs = window.location.href.replace(
          /^([^?]+)([^#]+)(.*)$/,
          '$1?' + qs + '$3'
        )

        if (qs != window.location.href) {
            history.pushState(null, '', qs)
        }
      },

      _add_block: function (block) {
        block.id = ++this.last_block_id
        this.blocks.push(block)
      },

      _get_block_div: function (block) {
        return $('#block-' + block.id)
      },

      _get_view_div: function (block, view) {
        // returns the jquery element for the div representing a view
        // TODO: use ids/class in html instead of searching like this
        let vi = block.views.indexOf(view)
        let views = $('#block-' + block.id + ' .card-section')
        return $(views[vi > -1 && vi < views.length ? vi : 0])
      },

      _get_group_from_query_string: function() {
        // return the value of &group query string param
        // returns 'declaration' if unspecified
        let ret = window.location.href.replace(
          /.*group=([^#&]+).*/,
          '$1'
        )
        if (ret == window.location) {
          ret = GROUP_DEFAULT;
        }
        return ret;
      },

      init_blocks: function () {
        let self = this
        // Create blocks from the 'blocks' param in the query strings
        // e.g. ?blocks=506:transcription,transcription;495:transcription
        let query_string_blocks = window.location.href.replace(
          /.*blocks=([^#&]+).*/,
          '$1'
        )
        if (query_string_blocks != window.location) {
          for (let block_info of query_string_blocks.split(';')) {
            if (block_info) {
              let parts = block_info.split('@')
              let sublocation = parts[1] || ''
              parts = parts[0].split(':')
              this._add_block({
                text: self.get_text_from_id_or_siglum(parts[0]),
                views: parts[1]
                  .split(',')
                  .map((view_type) => self._get_new_view_data(view_type)),
                comparative: false,
                sublocation: sublocation
              })
            }
          }
        }
        // Default blocks, if needed
        if (this.blocks.length < 1) {
          // block for the 'original copy'
          this._add_block({
            text: self.get_default_text(),
            views: [self._get_new_view_data()],
            comparative: false
          })
        }
        if (this.blocks.length < 2) {
          // placeholder block
          this._add_block({
            text: null,
            views: [
              self._get_new_view_data(
                'transcription',
                'placeholder',
                STATUS_FETCHED
              )
            ],
            comparative: false
          })
        }

        Vue.nextTick(function () {
          // Fundation JS re-initialisation
          $('.off-canvas-absolute:not(.foundation-initialised)').each(
            function () {
              $(this).addClass('foundation-initialised')
              new window.Foundation.OffCanvas($(this))
            }
          )
        })
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

      get_default_text: function () {
        return this.get_text_from_id_or_siglum(DEFAULT_SIGLUMS[this.group])
      },

      _get_new_view_data: function (view_type, chunk, status) {
        return {
          type: view_type || 'transcription',
          chunk: chunk || null,
          status: status === undefined ? STATUS_TO_FETCH : status,
          display_wregions: DISPLAY_WREGIONS_DEFAULT
        }
      },

      _after_chunk_loaded(block, view) {
        let self = this

        let $view = self._get_view_div(block, view)

        // when the user clicks a variant/reading in a region
        // we load the text of that variant in the other block/pane
        $view.find('.variants').on('click', '.variant', function (e) {
          let text_id = this.getAttribute('data-tid')

          // e.g. v-4 (4th v-region)
          let region_id = $(this).parent().data('parent-rid')

          // If in fullscreen, exit fullscreen
          // Force fullscreen classes off
          $view.parent().parent().parent().removeClass('off-canvas-fixed')
          $view.parent().removeClass('fullscreen-view')

          let text = self.get_text_from_id_or_siglum(text_id)
          self._load_other_text_in_other_block(block, text, region_id)
          e.stopPropagation()
        })

        // user click on sentence number
        $view.find('[data-dpt=sn]').on('click', function (e) {
          $view.find('.' + HIGHLIGHT_CLASS).removeClass(HIGHLIGHT_CLASS)
          $(this).addClass(HIGHLIGHT_CLASS)

          // e.g. s-4 (4th sentence)
          let region_id = this.getAttribute('data-rid')

          self._load_other_text_in_other_block(block, null, region_id)
          e.stopPropagation()
        })

        if (view.type === HISTOGRAM_VIEW) {
          // user click a histogram bar
          $view.find('[data-dpt-group]').on('click', function (e) {
            $view.find('.' + HIGHLIGHT_CLASS).removeClass(HIGHLIGHT_CLASS)
            $(this).addClass(HIGHLIGHT_CLASS)

            // for histogram bar we don't change the text in the other block
            let region_id = $(this).data('rid')
            self._load_other_text_in_other_block(block, null, region_id)
            e.stopPropagation()
          })
        } else {
          $view.find('[data-dpt-group]').each(function () {
            const group = $(this).data('dpt-group')
            const link = $(
              '<a class="view-type view-type-' + group + '">'
            ).html(group.substring(0, 1))

            // $(this).prepend(': ')
            $(this).prepend(link)
          })

          // user click region to go up the hierarchy: MS->V, V->W
          // it is region-based and will open the corresponding region
          // in the other block
          $view.find('[data-dpt-group] a').on('click', function (e) {
            const parent = $(this).parent()

            $view.find('.' + HIGHLIGHT_CLASS).removeClass(HIGHLIGHT_CLASS)
            parent.addClass(HIGHLIGHT_CLASS)

            // for a click on a region we open the current text
            let text = block.text
            if (parent.data('dpt-group') != block.text.type) {
              // or its parent
              text = text.parent
            }

            const region_id = parent.data('rid')
            self._load_other_text_in_other_block(block, text, region_id)
            e.stopPropagation()
          })
        }

        // hover on the variants
        $view.find('[data-related-id]').on('mouseover', function (e) {
          if ($(this).data('toggle') !== undefined) {
            e.stopPropagation()
            return
          }

          const relatedId = $(this).data('related-id')

          $(this).attr('data-toggle', relatedId)

          const el = $(`#${relatedId}`)

          $(el).addClass('dropdown-pane')
          $(el).attr('data-dropdown', '')
          $(el).attr('data-hover', true)
          $(el).attr('data-hover-pane', true)

          const w = WINDOW_INNER_WIDTH
          const x = e.clientX
          let alignment = 'left'

          if (x >= w / 4 && x <= w / 2) {
            alignment = 'right'
          } else if (x >= 3 * (w / 4)) {
            alignment = 'right'
          }

          const dropdown = new Foundation.Dropdown(el, {
            alignment: alignment
          })

          dropdown.toggle()

          e.stopPropagation()
        })

        // scroll to region/sublocation
        this.scroll_to_sublocation(block)
      },

      _load_other_text_in_other_block(source_block, other_text, region_id) {
        // Load other_text in another block than source_block.
        // If other_text is null, the other block will stay on the same text
        // and we only scroll to region_id.

        for (let other_block of this.blocks) {
          if (other_block != source_block) {
            if (!other_text && !other_block.text) {
                // in case other block has no text selected yet,
                // we select the same text as source
                other_text = source_block.text;
            }
            this.on_change_text(other_block, other_text, region_id)
            break
          }
        }
      }
    }
  })
})
