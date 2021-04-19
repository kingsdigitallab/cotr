<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
>
  <xsl:template match="/">
    <xsl:apply-templates select="/body" />
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

  <xsl:template match="span[@data-dpt='head'][@data-dpt-rend='emphasised']">
    <!-- W 'btnHeadingEmphasised': {'label': 'Heading (rubricated)', 'tei': '<head rend="emphasised">{}</head>'}, -->
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="p[.//span[@data-dpt='head']]">
    <!-- 'btnHeading': {'label': 'Heading (MS)', 'tei': '<head>{}</head>', 'color': TE_COLOR_DESCRIPTIVE}, -->
    <!-- 'btnSubHeading': {'label': 'Sub-heading (MS)', 'tei': '<head type="subheading">{}</head>', 'color': TE_COLOR_DESCRIPTIVE}, -->
    <head>
      <xsl:apply-templates select=".//span[@data-dpt='head']/@*"/>
      <xsl:apply-templates/>
    </head>
  </xsl:template>
  <xsl:template match="p//span[@data-dpt='head']">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="p[span[@data-dpt='sn']]">
    <!-- 'btnSentenceNumber': {'label': 'Sentence Number', 'tei': '<sn>{}</sn>', 'color': TE_COLOR_EDITORIAL}, -->
    <s n="{./span[@data-dpt='sn']}">
      <xsl:apply-templates select="./span[@data-dpt='sn']/@n"/>
      <xsl:apply-templates/>
    </s>
  </xsl:template>
  <xsl:template match="p/span[@data-dpt='sn']">
  </xsl:template>

  <xsl:template match="em|span[@data-dpt-lang='vernacular']">
    <!-- D 'btnVernacular': {'label': 'Vernacular', 'tei': '<seg lang="vernacular">{}</seg>', 'plain': 1}, -->
    <!-- TODO: best way to encode vernacular? -->
    <foreign xml:lang="ang"><xsl:apply-templates /></foreign>
  </xsl:template>

  <xsl:template match="span[@data-dpt-type='unsettled'][not(@data-related-id)]">
    <seg type="unsettled" subtype="{./@data-dpt-group}" n="{./@data-rid}">
      <xsl:apply-templates/>
    </seg>
  </xsl:template>
  <xsl:template match="span[@data-dpt-type='unsettled'][@data-related-id]">
    <!-- 'btnWUnsettled': {'label': 'W-Unsettled', 'tei': '<seg type="unsettled" group="work">{}</seg>'},-->
    <app n="{./@data-rid}">
      <xsl:apply-templates select="..//span[@id=(current()/@data-related-id)]/span[@class='variant']"/>
    </app>
  </xsl:template>
  <xsl:template match="span[@class='variants']">
  </xsl:template>
  <xsl:template match="span[@class='variant']">
    <rdg wit="{span[2]/text()}"><xsl:apply-templates select="span[@class='reading']"/></rdg>
  </xsl:template>
  <xsl:template match="span[@class='reading']">
    <!-- TODO: replace &#8709; with lacunae -->
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="span[@data-dpt='cn'][@data-dpt-type='editorial']">
    <!-- 'btnBlockNumber': {'label': 'Block Number', 'tei': '<cn type="editorial">{}</cn>', 'color': TE_COLOR_EDITORIAL}, -->
    <!-- TODO: should be a div, but hard to extract it from heading or sentence where it has been defined -->
    <milestone unit="block" n="{.}" />
  </xsl:template>

  <xsl:template match="span[@data-dpt='cn'][not(@data-dpt-type)]">
    <!-- 'btnChapterNumber': {'label': 'Chapter Number', 'tei': '<cn>{}</cn>', 'color': TE_COLOR_DESCRIPTIVE}, -->
    <rs type="chapter"><xsl:apply-templates /></rs>
  </xsl:template>

  <xsl:template match="strong">
    <!-- No agreed semantic, so we mute that mark-up. -->
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="span[@data-dpt-rend='color(ret)']">
    <!--'btnRedInk': {'label': 'Red Ink', 'tei': '<hi rend="color(ret)">{}</hi>', 'color': '#ffc9c9'},-->
    <hi rend="red"><xsl:apply-templates /></hi>
  </xsl:template>

  <xsl:template match="span[@data-dpt='newhand']">
    <!--'btnHandShift': {'label': 'New Hand', 'tei': '<newhand>{}</newhand>'},-->
    <handshift scribe="other" /><xsl:apply-templates /><handshift scribe="main" />
  </xsl:template>

  <xsl:template match="span[@class='no-text']">
    <xsl:apply-templates />
  </xsl:template>

  <!-- 'btnAddedAbove': {'label': 'Added (above)', 'tei': '<add place="above">{}</add>'}, -->
  <!--  'btnAddedInline': {'label': 'Added (inline)', 'tei': '<add place="inline">{}</add>'},-->
  <!--'btnDeletedStruck': {'label': 'Deleted (struck)', 'tei': '<del rend="strikethrough">{}</del>', 'plain': 1},-->
  <!--'btnHighlighted': {'label': 'Highlighted', 'tei': '<hi rend="highlight">{}</hi>'},-->
  <!--'btnSuperscripted': {'label': 'Superscripted', 'tei': '<hi rend="sup">{}</hi>', 'plain': 1},-->
  <!--'btnAuxiliary': {'label': 'Auxiliary', 'tei': '<div type="auxiliary">{}</div>', 'color': TE_COLOR_EDITORIAL, 'triggerName': 'onClickBtnAuxiliary'},-->

<!--

Unused constructs

U 'btnDeletedUnderpointed': {'label': 'Deleted (underpointed)', 'tei': '<del rend="underpointed">{}</del>'},
U 'btnDeletedErased': {'label': 'Deleted (erased)', 'tei': '<del rend="erased">{}</del>'},
U 'btnPartNumber': {'label': 'Part Number', 'tei': '<cn type="part">{}</cn>', 'color': TE_COLOR_DESCRIPTIVE},
U 'btnPageNumber': {'label': 'Locus', 'tei': '<location loctype="locus">{}</location>', 'color': TE_COLOR_DESCRIPTIVE},
U 'btnBlockNumber': {'label': 'Block Number', 'tei': '<cn type="editorial">{}</cn>', 'color': TE_COLOR_EDITORIAL},
U 'btnUnsettled': {'label': 'V-Unsettled', 'tei': '<seg type="unsettled">{}</seg>'},

-->

</xsl:stylesheet>
