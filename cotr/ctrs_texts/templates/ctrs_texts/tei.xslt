<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <body>
      <xsl:apply-templates />
    </body>
  </xsl:template>
  <xsl:template match="node()">
    <xsl:copy>
      <xsl:apply-templates select="node() | @*"/>
    </xsl:copy>
  </xsl:template>
  <xsl:template match="*[@data-dpt]">
    <xsl:element name="{@data-dpt}">
      <xsl:apply-templates select="node() | @*"/>
    </xsl:element>
  </xsl:template>
  <xsl:template match="@data-dpt">
  </xsl:template>
  <xsl:template match="@*">
    <xsl:choose>
      <xsl:when test="starts-with(name(.), 'data-dpt-')">
        <xsl:attribute name="{substring-after(name(.),'data-dpt-')}"><xsl:value-of select="."/></xsl:attribute>
      </xsl:when>
      <xsl:otherwise>
        <xsl:copy>
        </xsl:copy>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="p[span[@data-dpt='head']]">
    <head>
      <xsl:apply-templates select="node() | @*"/>
    </head>
  </xsl:template>
  <xsl:template match="p/span[@data-dpt='head']">
    <xsl:apply-templates select="node()"/>
  </xsl:template>

  <xsl:template match="p[span[@data-dpt='sn']]">
    <s n="{./span[@data-dpt='sn']}">
      <xsl:apply-templates select="./span[@data-dpt='sn']/@* | @*"/>
      <xsl:apply-templates select="node()"/>
    </s>
  </xsl:template>
  <xsl:template match="p/span[@data-dpt='sn']">
  </xsl:template>


  <!--
'btnHeadingEmphasised': {'label': 'Heading (rubricated)', 'tei': '<head rend="emphasised">{}</head>'},
'btnSubHeading': {'label': 'Sub-heading (MS)', 'tei': '<head type="subheading">{}</head>', 'color': TE_COLOR_DESCRIPTIVE},
'btnPartNumber': {'label': 'Part Number', 'tei': '<cn type="part">{}</cn>', 'color': TE_COLOR_DESCRIPTIVE},
'btnChapterNumber': {'label': 'Chapter Number', 'tei': '<cn>{}</cn>', 'color': TE_COLOR_DESCRIPTIVE},
# no longer needed
'btnPageNumber': {'label': 'Locus', 'tei': '<location loctype="locus">{}</location>', 'color': TE_COLOR_DESCRIPTIVE},

'btnBlockNumber': {'label': 'Block Number', 'tei': '<cn type="editorial">{}</cn>', 'color': TE_COLOR_EDITORIAL},
D 'btnSentenceNumber': {'label': 'Sentence Number', 'tei': '<sn>{}</sn>', 'color': TE_COLOR_EDITORIAL},
'btnAuxiliary': {'label': 'Auxiliary', 'tei': '<div type="auxiliary">{}</div>', 'color': TE_COLOR_EDITORIAL, 'triggerName': 'onClickBtnAuxiliary'},

'btnUnsettled': {'label': 'V-Unsettled', 'tei': '<seg type="unsettled">{}</seg>'},
'btnWUnsettled': {'label': 'W-Unsettled', 'tei': '<seg type="unsettled" group="work">{}</seg>'},

'btnAddedAbove': {'label': 'Added (above)', 'tei': '<add place="above">{}</add>'},
'btnAddedInline': {'label': 'Added (inline)', 'tei': '<add place="inline">{}</add>'},
'btnDeletedStruck': {'label': 'Deleted (struck)', 'tei': '<del rend="strikethrough">{}</del>', 'plain': 1},
'btnDeletedErased': {'label': 'Deleted (erased)', 'tei': '<del rend="erased">{}</del>'},
'btnDeletedUnderpointed': {'label': 'Deleted (underpointed)', 'tei': '<del rend="underpointed">{}</del>'},
'btnRedInk': {'label': 'Red Ink', 'tei': '<hi rend="color(ret)">{}</hi>', 'color': '#ffc9c9'},
'btnHighlighted': {'label': 'Highlighted', 'tei': '<hi rend="highlight">{}</hi>'},
'btnSuperscripted': {'label': 'Superscripted', 'tei': '<hi rend="sup">{}</hi>', 'plain': 1},
'btnHandShift': {'label': 'New Hand', 'tei': '<newhand>{}</newhand>'},

'btnVernacular': {'label': 'Vernacular', 'tei': '<seg lang="vernacular">{}</seg>', 'plain': 1},
  -->

</xsl:stylesheet>
