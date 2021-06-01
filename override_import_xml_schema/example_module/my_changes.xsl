<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rng="http://relaxng.org/ns/structure/1.0">
  <!-- For explanation see comments in my_changes_view.xsl. -->
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>
  <xsl:template match="rng:element[@name='record']">
      <xsl:copy>
          <xsl:apply-templates select="@*|node()"/>
          <rng:optional><rng:attribute name="hello"/></rng:optional>
      </xsl:copy>
  </xsl:template>
</xsl:stylesheet>
