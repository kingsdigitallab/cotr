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
  <xsl:template match="p[span[@data-dpt='sn']]">
    <s n="{./span[@data-dpt='sn']}">
      <xsl:apply-templates select="./span[@data-dpt='sn']/@* | @*"/>
      <xsl:apply-templates select="node()"/>
    </s>
  </xsl:template>
  <xsl:template match="p/span[@data-dpt='head']">
    <xsl:apply-templates select="node()"/>
  </xsl:template>
  <xsl:template match="p/span[@data-dpt='sn']">
  </xsl:template>
</xsl:stylesheet>
